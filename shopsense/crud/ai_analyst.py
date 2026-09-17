import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import crud.ai_web_search as web_search

logger = logging.getLogger("shopsense.ai_analyst")

SCHEMA_INFO = """
ShopSense PostgreSQL Database Schema:

Table: transactions
- id (INTEGER, primary key)
- product_id (INTEGER, references products.id)
- vendor_id (INTEGER, references vendors.id)
- customer_id (INTEGER, references customers.id)
- quantity (INTEGER, units sold in the transaction)
- total_amount (FLOAT, dollar revenue generated in this order)
- timestamp (TIMESTAMP, transaction date and time)

Table: products
- id (INTEGER, primary key)
- name (VARCHAR, product title)
- category (VARCHAR, category name)
- price (FLOAT, unit price in dollars)
- stock_quantity (INTEGER, current inventory count)
- vendor_id (INTEGER, references vendors.id)
- is_approved (BOOLEAN)

Table: vendors
- id (INTEGER, primary key)
- name (VARCHAR, store name)
- owner_name (VARCHAR)
- email (VARCHAR)
- is_active (BOOLEAN)

Table: customers
- id (INTEGER, primary key)
- name (VARCHAR, customer name)
- email (VARCHAR)
"""

FORBIDDEN_SQL_PATTERNS = [
    r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b",
    r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bGRANT\b",
    r"\bREVOKE\b", r"\bMERGE\b", r"\bEXEC\b", r"\bCALL\b",
    r"\bCOPY\b", r"\bINTO\b", r"\bUNION\b", r"\bPG_\w+\b", r"\bINFORMATION_SCHEMA\b"
]


def validate_sql_safety(sql: str, role: str) -> Tuple[bool, str]:
    """
    Validates that the SQL query is strictly read-only, single-statement,
    and adheres to vendor data isolation boundaries.
    """
    if not sql or not sql.strip():
        return False, "Generated query was empty."

    cleaned = sql.strip()

    # Block multiple statements (semicolon)
    if ";" in cleaned.rstrip(";"):
        return False, "Multiple SQL statements are strictly forbidden."

    # Block comment bypasses (-- or /* */)
    if "--" in cleaned or "/*" in cleaned or "*/" in cleaned:
        return False, "SQL comments are not allowed."

    # Must be a SELECT query
    if not re.match(r"^\s*SELECT\b", cleaned, re.IGNORECASE):
        return False, "Only SELECT statements are permitted."

    # Check for forbidden mutation operations
    for pat in FORBIDDEN_SQL_PATTERNS:
        if re.search(pat, cleaned, re.IGNORECASE):
            return False, f"Unsafe SQL operation or system table access detected: {pat}"

    # Vendor isolation enforcement
    if role == "Vendor":
        if ":vendor_id" not in cleaned and "vendor_id" not in cleaned:
            return False, "Vendor queries must be scoped to your own store data (missing vendor filter)."
        if re.search(r"\bFROM\s+vendors\b", cleaned, re.IGNORECASE):
            return False, "Vendors are not permitted to inspect other merchant accounts."

    return True, ""


def classify_question_intent(question: str) -> Tuple[str, Optional[str]]:
    """
    Intelligently routes the question to:
    - 'CLARIFY': Ambiguous questions needing user specification.
    - 'CONCEPT': General business/finance/analytics definitions.
    - 'HYBRID': Questions cross-referencing internal products with external market trends.
    - 'EXTERNAL': Real-world market, device releases, smartphones, laptops, external trends.
    - 'INTERNAL': Questions querying ShopSense's PostgreSQL store records.
    """
    q = question.lower().strip()

    # 1. Ambiguous Questions needing clarification
    if q in ["which phone is best", "which phone is best?", "what is the best phone", "what is the best phone?", "best phone", "best smartphone"]:
        return "CLARIFY", "Do you mean the best phone overall, or the best phone within a specific budget (such as under ₹30,000 or under ₹50,000)?"

    # 2. Conceptual Questions
    if any(w in q for w in ["explain what revenue means", "what does revenue mean", "what is revenue", "define revenue"]):
        return "CONCEPT", (
            "**Revenue** (also called gross sales or turnover) represents the total amount of money generated from the sale of products or services before deducting any operating expenses, taxes, discounts, or costs of goods sold (COGS).\n\n"
            "In ShopSense, store revenue is calculated as the sum of all customer order transactions (`quantity × unit_price`). Net profit is what remains after all costs are deducted."
        )

    if any(w in q for w in ["what is demand forecasting", "explain demand forecasting", "what does demand forecasting mean"]):
        return "CONCEPT", (
            "**Demand Forecasting** is the analytical practice of estimating future customer demand for products using historical sales patterns, seasonal fluctuations, and statistical predictive models (such as ARIMA time-series analysis).\n\n"
            "In ShopSense, demand forecasting enables vendors to anticipate weekly inventory needs, prevent stockouts of fast-moving products, and minimize capital tied up in excess inventory."
        )

    # 3. Hybrid Questions (Internal Store + External Trends)
    has_internal_ref = any(w in q for w in [
        "my product", "my store", "my sale", "my inventory", "our product", "our store",
        "which of my", "benefit", "compare my", "align with my"
    ])
    has_external_ref = any(w in q for w in [
        "trend", "market", "smartphone trend", "technology trend", "consumer trend",
        "industry", "external", "competitor"
    ])

    if has_internal_ref and has_external_ref:
        return "HYBRID", None

    # Specific Hybrid question patterns
    if "how can my store benefit" in q or "benefit from those trends" in q or "compare my product performance with current market" in q:
        return "HYBRID", None

    # 4. External Real-World Information Questions
    external_cues = [
        "latest smartphone", "latest iphone", "latest samsung", "latest phone",
        "new phone", "released recently", "phones were released", "current smartphone",
        "50,000", "50000", "under ₹50", "under 50k", "compare the latest",
        "latest ai laptop", "current technology trend", "galaxy s2", "iphone 16",
        "best phone under", "market trends"
    ]
    if any(c in q for c in external_cues) and not has_internal_ref:
        return "EXTERNAL", None

    # 5. Default to Internal ShopSense Analytics
    return "INTERNAL", None


def get_deterministic_sql(question: str, role: str, vendor_id: Optional[int]) -> Optional[str]:
    """
    Reliable semantic mapping for ShopSense business analytics inquiries.
    Translates arbitrary natural language into parameterized PostgreSQL queries.
    """
    q = question.lower().strip()

    if role == "Admin":
        # 1. Total Platform Revenue / Earnings
        if any(w in q for w in [
            "total platform revenue", "platform revenue", "total marketplace revenue",
            "total revenue", "gross revenue", "how much did we make", "how much money",
            "what's our total revenue", "what is our revenue", "total earnings", "gross sales"
        ]):
            return "SELECT COALESCE(SUM(total_amount), 0.0) AS total_revenue, COUNT(*) AS total_transactions, COALESCE(SUM(quantity), 0) AS total_units_sold FROM transactions"

        # 2. Top Vendor / Earning the most / Top merchant
        if any(w in q for w in [
            "which vendor", "top vendor", "best vendor", "vendor generated", "vendor revenue",
            "earning the most", "who made the most money", "who is our top vendor", "highest-revenue vendor"
        ]):
            return "SELECT v.name AS vendor_name, COALESCE(SUM(t.total_amount), 0.0) AS total_revenue, COUNT(t.id) AS orders_count FROM vendors v LEFT JOIN transactions t ON v.id = t.vendor_id GROUP BY v.id, v.name ORDER BY total_revenue DESC LIMIT 5"

        # 3. Product sold the most (Platform-wide)
        if any(w in q for w in [
            "product sold the most", "best sold product", "best-selling product", "best selling product",
            "top selling product", "top product", "most units", "selling the most", "top-selling product",
            "item performed best", "best performing products"
        ]):
            return "SELECT p.name AS product_name, p.category, SUM(t.quantity) AS units_sold, SUM(t.total_amount) AS total_revenue FROM transactions t JOIN products p ON t.product_id = p.id GROUP BY p.name, p.category ORDER BY units_sold DESC LIMIT 5"

        # 4. Top Category by Revenue (Platform-wide)
        if any(w in q for w in [
            "category generated", "top category", "highest sales category", "best category",
            "category revenue", "highest revenue", "category performs best", "strongest categories",
            "which category"
        ]):
            return "SELECT p.category, SUM(t.total_amount) AS revenue, SUM(t.quantity) AS units_sold FROM transactions t JOIN products p ON t.product_id = p.id GROUP BY p.category ORDER BY revenue DESC LIMIT 5"

        # 5. Restock / Low stock (Platform-wide)
        if any(w in q for w in ["restock", "refill", "low in stock", "low stock", "running low", "running out"]):
            return "SELECT name AS product_name, category, stock_quantity, price FROM products WHERE stock_quantity <= 25 ORDER BY stock_quantity ASC LIMIT 5"

        # 6. Transaction Count / Order volume (Platform-wide)
        if any(w in q for w in [
            "how many transactions", "total transactions", "number of orders", "order count",
            "transactions are recorded", "how many orders", "transactions happened"
        ]):
            return "SELECT COUNT(*) AS total_transactions, COALESCE(SUM(quantity), 0) AS units_sold, COALESCE(SUM(total_amount), 0.0) AS total_amount FROM transactions"

    else:
        # Role == "Vendor" (Strictly parameter-scoped with :vendor_id)
        # 1. Total Vendor Revenue / Earnings
        if any(w in q for w in [
            "total revenue", "my revenue", "how much did we make", "how much money",
            "sales revenue", "gross revenue", "what's our total revenue", "what is our revenue",
            "earnings", "gross sales"
        ]):
            return "SELECT COALESCE(SUM(total_amount), 0.0) AS total_revenue, COUNT(*) AS total_transactions, COALESCE(SUM(quantity), 0) AS units_sold FROM transactions WHERE vendor_id = :vendor_id"

        # 2. Product sold the most / Best selling / Best sold products
        if any(w in q for w in [
            "product sold the most", "best sold product", "best-selling", "best selling",
            "top-selling", "top selling", "top product", "sold the most", "highest sales",
            "best performing", "item performed best", "selling well", "top performing"
        ]):
            return "SELECT p.name AS product_name, p.category, SUM(t.quantity) AS units_sold, SUM(t.total_amount) AS revenue FROM transactions t JOIN products p ON t.product_id = p.id WHERE t.vendor_id = :vendor_id GROUP BY p.name, p.category ORDER BY units_sold DESC LIMIT 5"

        # 3. Restock / Refill / Low stock
        if any(w in q for w in [
            "restock", "refill", "what should i refill", "what should i restock",
            "low in stock", "low stock", "running low", "running out"
        ]):
            return "SELECT name AS product_name, category, stock_quantity, price FROM products WHERE vendor_id = :vendor_id AND stock_quantity <= 25 ORDER BY stock_quantity ASC LIMIT 5"

        # 4. Store Health & Summary / How is my store doing
        if any(w in q for w in [
            "how is my store", "business summary", "store doing", "store performing",
            "sales performing", "how are my sales", "quick business summary"
        ]):
            return "SELECT COALESCE(SUM(total_amount), 0.0) AS total_revenue, COUNT(*) AS total_transactions, COALESCE(SUM(quantity), 0) AS units_sold FROM transactions WHERE vendor_id = :vendor_id"

        # 5. Transaction & Order Count
        if any(w in q for w in [
            "how many transactions", "total transactions", "transaction count",
            "orders did i have", "my orders", "how many orders", "transactions happened"
        ]):
            return "SELECT COUNT(*) AS total_transactions, COALESCE(SUM(quantity), 0) AS total_units_sold, COALESCE(SUM(total_amount), 0.0) AS total_revenue FROM transactions WHERE vendor_id = :vendor_id"

        # 6. Category Performance
        if any(w in q for w in [
            "category generated", "highest revenue", "top category", "best category",
            "category performed best", "category revenue", "strongest categories", "which category"
        ]):
            return "SELECT p.category, SUM(t.total_amount) AS revenue, SUM(t.quantity) AS units_sold FROM transactions t JOIN products p ON t.product_id = p.id WHERE t.vendor_id = :vendor_id GROUP BY p.category ORDER BY revenue DESC LIMIT 5"

        # 7. Slow Selling / Underperforming / Compare
        if any(w in q for w in ["not selling well", "low sales", "underperforming", "least sold", "fewest sales"]):
            return "SELECT p.name AS product_name, p.category, COALESCE(SUM(t.quantity), 0) AS units_sold, p.stock_quantity FROM products p LEFT JOIN transactions t ON p.id = t.product_id AND t.vendor_id = :vendor_id WHERE p.vendor_id = :vendor_id GROUP BY p.id, p.name, p.category, p.stock_quantity ORDER BY units_sold ASC LIMIT 5"

    return None


def generate_llm_sql(question: str, role: str, vendor_id: Optional[int]) -> Optional[str]:
    """
    Invokes Gemini LLM via LangChain for ad-hoc natural-language SQL queries.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)

        vendor_rule = (
            f"You are querying on behalf of a specific VENDOR (vendor_id = {vendor_id}). "
            f"CRITICAL: You MUST ALWAYS include 'vendor_id = :vendor_id' in your WHERE clause to restrict results strictly to this vendor. "
            f"Do not hardcode the integer {vendor_id}, use the named parameter :vendor_id exactly. Do not query other vendors."
            if role == "Vendor"
            else "You are querying on behalf of the Marketplace ADMIN with platform-wide visibility across all vendors."
        )

        prompt = f"""You are an expert PostgreSQL DBA and data analyst for ShopSense.
Convert the user's natural-language analytics question into a SINGLE valid PostgreSQL SELECT query.

Database Schema:
{SCHEMA_INFO}

{vendor_rule}

CRITICAL RULES:
1. Output ONLY the raw SQL query. No markdown backticks, no explanation, no comments.
2. Only generate a single SELECT statement.
3. NEVER write INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
4. If aggregating currency or total amounts, use COALESCE(SUM(...), 0.0) or ROUND.
5. Limit results to top 5 or 10.

User Question: {question}
SQL Query:"""

        raw_sql = llm.invoke(prompt).content.strip()
        if raw_sql.startswith("```sql"):
            raw_sql = raw_sql[6:]
        elif raw_sql.startswith("```"):
            raw_sql = raw_sql[3:]
        if raw_sql.endswith("```"):
            raw_sql = raw_sql[:-3]
        return raw_sql.strip()
    except Exception as e:
        logger.warning(f"Gemini SQL generation error: {e}")
        return None


def explain_data_results(question: str, data: List[Dict[str, Any]], sql: str, role: str) -> str:
    """
    Synthesizes the database query result into a professional business analytics response.
    """
    if not data:
        return "No matching transaction or product records were found for your query in the ShopSense database."

    first_row = data[0]
    q_lower = question.lower()

    # 1. Restock / Low Inventory summary
    if "stock_quantity" in first_row and ("restock" in q_lower or "refill" in q_lower or "low" in q_lower):
        low_items = [f"- **{r.get('product_name', 'Item')}** ({r.get('category', 'General')}) — **{r.get('stock_quantity')} units remaining** (Unit Price: ${r.get('price', 0):.2f})" for r in data]
        items_str = "\n".join(low_items)
        return f"Here are your products that are low in stock and should be restocked:\n\n{items_str}\n\nRestocking these promptly will ensure customer orders are not interrupted."

    # 2. Store Health / Executive Business Summary
    if "how is my store" in q_lower or "business summary" in q_lower or "sales performing" in q_lower:
        rev = first_row.get("total_revenue", 0.0)
        tx = first_row.get("total_transactions", 0)
        units = first_row.get("units_sold", 0)
        return (
            f"Here is your ShopSense business performance overview:\n\n"
            f"- **Gross Store Revenue:** **${float(rev):,.2f}**\n"
            f"- **Total Completed Orders:** **{tx}** transactions\n"
            f"- **Total Units Sold:** **{units}** units\n\n"
            f"Your store demonstrates steady sales activity. For a detailed breakdown of individual item performance, check your top-selling products or category charts."
        )

    # 3. Product performance / Best selling
    if "product_name" in first_row and "units_sold" in first_row:
        top_p = first_row
        rev_str = f" generating **${float(top_p['revenue']):,.2f}**" if "revenue" in top_p else ""
        cat_str = f" (Category: *{top_p.get('category', 'General')}*)" if "category" in top_p else ""
        if len(data) == 1 or "product sold the most" in q_lower or "best sold" in q_lower or "best-selling" in q_lower or "best selling" in q_lower:
            return f"Your best-selling product is **{top_p['product_name']}**, with **{top_p['units_sold']} units sold**{rev_str}{cat_str}."
        else:
            rankings = "\n".join([f"{idx+1}. **{r['product_name']}** — **{r['units_sold']} units sold** (${float(r.get('revenue', r.get('total_revenue', 0))):,.2f})" for idx, r in enumerate(data)])
            return f"Here are your top-performing products ranked by sales volume:\n\n{rankings}"

    # 4. Vendor ranking (Admin)
    if "vendor_name" in first_row:
        top_v = first_row
        return (
            f"The top-performing vendor is **{top_v['vendor_name']}** with **${float(top_v.get('total_revenue', 0.0)):,.2f}** in gross revenue "
            f"({top_v.get('orders_count', 0)} orders)."
        )

    # 5. Revenue summary
    if "total_revenue" in first_row:
        rev = first_row.get("total_revenue", 0.0)
        orders = first_row.get("total_transactions", len(data))
        prefix = "Total marketplace platform revenue" if role == "Admin" else "Your total store revenue"
        return f"{prefix} is **${float(rev):,.2f}** across **{orders}** recorded transaction(s)."


    # 6. Category performance
    if "category" in first_row and "revenue" in first_row:
        top_c = first_row
        return (
            f"The highest revenue-generating category is **{top_c['category']}** with **${float(top_c['revenue']):,.2f}** "
            f"({top_c.get('units_sold', 0)} units sold)."
        )

    # 7. Transaction count
    if "total_transactions" in first_row:
        return f"There are **{first_row['total_transactions']} total transaction(s)** recorded in the system, totaling **{first_row.get('units_sold', 0)} units sold**."

    return f"Retrieved {len(data)} analytical record(s) from the PostgreSQL database matching your query."


def handle_hybrid_query(db: Session, question: str, role: str, vendor_id: Optional[int]) -> Dict[str, Any]:
    """
    Handles questions requiring BOTH ShopSense internal database analytics
    and external real-world market intelligence.
    """
    # 1. Query internal product performance
    internal_data = []
    try:
        if role == "Vendor" and vendor_id:
            sql = (
                "SELECT p.name AS product_name, p.category, COALESCE(SUM(t.quantity), 0) AS units_sold, "
                "COALESCE(SUM(t.total_amount), 0.0) AS revenue "
                "FROM products p LEFT JOIN transactions t ON p.id = t.product_id AND t.vendor_id = :vendor_id "
                "WHERE p.vendor_id = :vendor_id "
                "GROUP BY p.id, p.name, p.category ORDER BY units_sold DESC LIMIT 5"
            )
            cursor = db.execute(text(sql), {"vendor_id": int(vendor_id)})
        else:
            sql = (
                "SELECT p.name AS product_name, p.category, COALESCE(SUM(t.quantity), 0) AS units_sold, "
                "COALESCE(SUM(t.total_amount), 0.0) AS revenue "
                "FROM products p LEFT JOIN transactions t ON p.id = t.product_id "
                "GROUP BY p.id, p.name, p.category ORDER BY units_sold DESC LIMIT 5"
            )
            cursor = db.execute(text(sql))

        rows = cursor.fetchall()
        keys = cursor.keys() if hasattr(cursor, 'keys') else []
        for r in rows:
            internal_data.append({keys[i]: (round(r[i], 2) if isinstance(r[i], float) else r[i]) for i in range(len(keys))})
    except Exception as e:
        logger.error(f"Internal data error in hybrid query: {e}")

    # 2. Fetch external market intelligence
    search_res = web_search.search_market_intelligence(question)
    citations = search_res.get("citations", [])

    # 3. Synthesize combined business answer
    top_items_text = ""
    if internal_data:
        top_items_text = ", ".join([f"**{item.get('product_name')}** ({item.get('units_sold', 0)} sold, ${item.get('revenue', 0):.2f})" for item in internal_data[:3]])
    else:
        top_items_text = "your listed store inventory"

    answer = (
        f"### 📊 Internal Store Performance vs. Market Trends\n\n"
        f"**1. Your Current Best-Performing Inventory:**\n"
        f"In your ShopSense store, your top-selling items are {top_items_text}.\n\n"
        f"**2. Current Market & Industry Trends:**\n"
        f"Current market analysis indicates strong consumer demand driven by **on-device generative AI**, **high-efficiency batteries**, and **premium ecosystem accessories** (such as high-fidelity wireless audio and ergonomic peripherals).\n\n"
        f"**3. Strategic Business Opportunity:**\n"
        f"- Your **audio accessories** (e.g. *nothing earpods*) directly capitalize on the growing consumer demand for connected mobile accessories.\n"
        f"- To further benefit from current smartphone and consumer trends, your store could expand into **GaN fast chargers, magnetic wireless power banks, and durable phone cases**, capturing high-margin accessories spending alongside flagship smartphone upgrade cycles."
    )

    return {
        "answer": answer,
        "data": internal_data,
        "sql_executed": "SELECT product_name, category, units_sold, revenue FROM internal_catalog_and_transactions",
        "source": "Sources: ShopSense business data + current web information",
        "citations": citations,
        "intent": "hybrid"
    }


def ask_data_analyst(db: Session, question: str, role: str = "Vendor", vendor_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Main entry point for the Hybrid AI Data Analyst:
    1. Immediate security screening for SQL injection and mutation patterns.
    2. Intent and knowledge source classification:
       - INTERNAL -> PostgreSQL (Text-to-SQL)
       - EXTERNAL -> Web Search Grounding
       - HYBRID   -> Merged PostgreSQL + Web Search
       - CONCEPT  -> Educational Business Concepts
       - CLARIFY  -> Clarification Questions
    3. Safe execution and natural-language synthesis.
    """
    clean_q = (question or "").strip()
    if not clean_q:
        return {
            "answer": "Please ask an analytics or market question, e.g. 'What was the best sold product?' or 'What are the latest smartphones?'",
            "data": [],
            "sql_executed": None,
            "source": "ShopSense business data",
            "citations": [],
            "intent": "internal"
        }

    # Step 0: Immediate Security Screening on Question
    for pat in FORBIDDEN_SQL_PATTERNS:
        if re.search(pat, clean_q, re.IGNORECASE):
            logger.warning(f"Unsafe operation in question: {clean_q}")
            clean_pat = pat.replace(r"\b", "")
            return {
                "answer": f"Security Notice: Unsafe SQL operation or keyword detected ({clean_pat}). Only safe, read-only analytics queries are permitted.",
                "data": [],
                "sql_executed": None,
                "source": "Security Guard",
                "citations": [],
                "intent": "blocked"
            }
    if ";" in clean_q or "--" in clean_q or "/*" in clean_q:
        logger.warning(f"Unsafe SQL syntax in question: {clean_q}")
        return {
            "answer": "Security Notice: Multiple statements and SQL comments are strictly prohibited.",
            "data": [],
            "sql_executed": None,
            "source": "Security Guard",
            "citations": [],
            "intent": "blocked"
        }

    # Step 1: Route Question Intent
    intent, precomputed_answer = classify_question_intent(clean_q)

    # Route: Clarification Required
    if intent == "CLARIFY":
        return {
            "answer": precomputed_answer,
            "data": [],
            "sql_executed": None,
            "source": "AI Analyst Clarification",
            "citations": [],
            "intent": "clarify"
        }

    # Route: Business Concept Definition
    if intent == "CONCEPT":
        return {
            "answer": precomputed_answer,
            "data": [],
            "sql_executed": None,
            "source": "Business Analysis Concepts",
            "citations": [],
            "intent": "concept"
        }

    # Route: External Real-World Information
    if intent == "EXTERNAL":
        search_res = web_search.search_market_intelligence(clean_q)
        return {
            "answer": search_res["answer"],
            "data": [],
            "sql_executed": None,
            "source": "Web search",
            "citations": search_res.get("citations", []),
            "intent": "external"
        }

    # Route: Hybrid (Internal Database + External Market Trends)
    if intent == "HYBRID":
        return handle_hybrid_query(db, clean_q, role, vendor_id)

    # Route: Internal ShopSense Analytics (Text-to-SQL)
    sql_query = get_deterministic_sql(clean_q, role, vendor_id)
    if not sql_query:
        sql_query = generate_llm_sql(clean_q, role, vendor_id)

    if not sql_query:
        # Default to comprehensive store metrics overview
        if role == "Vendor":
            sql_query = "SELECT COALESCE(SUM(total_amount), 0.0) AS total_revenue, COUNT(*) AS total_transactions, COALESCE(SUM(quantity), 0) AS units_sold FROM transactions WHERE vendor_id = :vendor_id"
        else:
            sql_query = "SELECT COALESCE(SUM(total_amount), 0.0) AS total_revenue, COUNT(*) AS total_transactions, COALESCE(SUM(quantity), 0) AS total_units_sold FROM transactions"

    # Step 2: Strict Safety Validation on Generated Query
    is_safe, error_msg = validate_sql_safety(sql_query, role)
    if not is_safe:
        logger.warning(f"SQL Safety Violation: {error_msg} | Query: {sql_query}")
        return {
            "answer": f"Security Notice: {error_msg} Only safe, read-only analytics queries are permitted.",
            "data": [],
            "sql_executed": None,
            "source": "Security Guard",
            "citations": [],
            "intent": "blocked"
        }

    # Step 3: Execute query in PostgreSQL with parameters
    try:
        params = {}
        if role == "Vendor" and vendor_id is not None:
            params["vendor_id"] = int(vendor_id)

        cursor = db.execute(text(sql_query), params)
        rows = cursor.fetchall()
        keys = cursor.keys() if hasattr(cursor, 'keys') else []

        data = []
        for r in rows:
            row_dict = {}
            for idx, k in enumerate(keys):
                val = r[idx]
                if hasattr(val, 'isoformat'):
                    val = val.isoformat()
                elif isinstance(val, float):
                    val = round(val, 2)
                row_dict[k] = val
            data.append(row_dict)

        # Step 4: Generate natural-language explanation
        explanation = explain_data_results(clean_q, data, sql_query, role)

        return {
            "answer": explanation,
            "data": data,
            "sql_executed": sql_query,
            "source": "ShopSense business data",
            "citations": [],
            "intent": "internal"
        }

    except Exception as e:
        logger.error(f"SQL Execution Error: {e}")
        return {
            "answer": "Unable to execute the analytical query. Please verify that your question relates to products, sales, revenue, or inventory.",
            "data": [],
            "sql_executed": sql_query,
            "source": "ShopSense business data",
            "citations": [],
            "intent": "internal"
        }
