import os
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from models import Product

logger = logging.getLogger("shopsense.ai_assistant")

# Common general shopping/catalog phrases that mean "what is available to buy"
GENERAL_CATALOG_PATTERNS = [
    r"\bwhat\b.*\b(available|in stock|buy|have|sell)\b",
    r"\bwhat\s+(is|are|do\s+you\s+have)\s+available\b",
    r"\bwhat('?s|\s+is|\s+are)\s+available\b",
    r"\bavailable\s+products\b",
    r"\bwhat\s+can\s+(i|we)\s+buy\b",
    r"\bshow\s+(me\s+)?(the\s+)?products\b",
    r"\blist\s+(the\s+)?products\b",
    r"\bwhat\s+products\b",
    r"\bwhat\s+items\b",
    r"\bshow\s+catalog\b",
    r"\ball\s+products\b",
    r"\ball\s+items\b",
    r"\bstore\s+items\b",
    r"\bwhat\s+do\s+you\s+(have|sell)\b",
    r"\brecommend\b",
    r"\bpopular\s+products\b",
    r"\bbest\s+products\b"
]

# Low stock / restocking trigger patterns
LOW_STOCK_PATTERNS = [
    r"\blow\s+in\s+stock\b",
    r"\blow\s+stock\b",
    r"\brunning\s+out\b",
    r"\brunning\s+low\b",
    r"\blimited\s+stock\b",
    r"\bneed\s+restocking\b",
    r"\bneeds\s+restock\b",
    r"\brestock\b",
    r"\blow\s+inventory\b",
    r"\balmost\s+out\b",
    r"\bfew\s+left\b"
]

# Price inquiry trigger patterns
PRICE_PATTERNS = [
    r"\bhow\s+much\b",
    r"\bprice\b",
    r"\bcost\b",
    r"\brate\b",
    r"\bhow\s+expensive\b"
]

# Availability inquiry trigger patterns
AVAILABILITY_PATTERNS = [
    r"\bis\s+.*\s+available\b",
    r"\bis\s+.*\s+in\s+stock\b",
    r"\bdo\s+you\s+have\b",
    r"\bhow\s+many\b",
    r"\bstock\b"
]

# Words that indicate a question is related to shopping/e-commerce
COMMERCE_KEYWORDS = {
    "product", "products", "item", "items", "buy", "purchase", "price", "prices",
    "cost", "stock", "available", "availability", "catalog", "shop", "store",
    "sell", "order", "orders", "inventory", "brand", "category", "categories",
    "laptop", "footwear", "shoe", "shoes", "sandal", "sandals", "slip", "jeans",
    "earpod", "earpods", "earbud", "earbuds", "audio", "bag", "bags", "handbag",
    "handbags", "leather", "bottle", "water", "electronics", "tech"
}


def is_unrelated_query(q: str, products: List[Product]) -> bool:
    """
    Checks if a query is completely unrelated to ShopSense e-commerce catalog.
    """
    words = set(re.findall(r'\b\w+\b', q))

    # Check if any product name, category, or tag word appears in the query
    for p in products:
        p_words = set(re.findall(r'\b\w+\b', f"{p.name} {p.category} {p.tags}".lower()))
        if words.intersection(p_words):
            return False

    # Check if any e-commerce keywords appear
    if words.intersection(COMMERCE_KEYWORDS):
        return False

    # Check for general catalog patterns
    for pat in GENERAL_CATALOG_PATTERNS + LOW_STOCK_PATTERNS + PRICE_PATTERNS:
        if re.search(pat, q):
            return False

    return True


def retrieve_relevant_products(db: Session, question: str, top_k: int = 6) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Retrieves candidate products from PostgreSQL using multi-intent semantic & lexical matching.
    Returns (retrieved_products, intent_metadata).
    """
    if not question or not question.strip():
        return [], {"intent": "empty"}

    q = question.lower().strip()
    words = set(re.findall(r'\b\w+\b', q))

    # Read-only fetch of active products from PostgreSQL
    products = db.query(Product).filter(Product.is_approved == True).all()
    if not products:
        return [], {"intent": "no_products_in_db"}

    # Check if query is unrelated to ShopSense store
    if is_unrelated_query(q, products):
        return [], {"intent": "unrelated"}

    # Intent detection
    is_low_stock = any(re.search(pat, q) for pat in LOW_STOCK_PATTERNS)
    is_price_query = any(re.search(pat, q) for pat in PRICE_PATTERNS)
    is_avail_query = any(re.search(pat, q) for pat in AVAILABILITY_PATTERNS)
    is_general_catalog = any(re.search(pat, q) for pat in GENERAL_CATALOG_PATTERNS)

    intent_meta = {
        "is_low_stock": is_low_stock,
        "is_price_query": is_price_query,
        "is_avail_query": is_avail_query,
        "is_general_catalog": is_general_catalog,
        "target_product": None
    }

    # Low Stock Intent
    if is_low_stock:
        low_items = [p for p in products if 0 < p.stock_quantity <= 20]
        results = [serialize_product(p) for p in low_items]
        return results, intent_meta

    # Check for specific product name match first (e.g. "handbag", "laptop", "footwear", "nothing earpods")
    scored_products = []
    for p in products:
        p_name = (p.name or "").lower()
        p_cat = (p.category or "").lower()
        p_desc = (p.description or "").lower()
        p_tags = (p.tags or "").lower()

        score = 0

        # Exact match of product name in query
        if p_name and p_name in q:
            score += 25

        # Word overlap with product name
        name_words = set(re.findall(r'\b\w+\b', p_name))
        name_overlap = words.intersection(name_words)
        score += len(name_overlap) * 8

        # Category match
        cat_words = set(re.findall(r'\b\w+\b', p_cat))
        cat_overlap = words.intersection(cat_words)
        if p_cat and p_cat in q:
            score += 15
        elif cat_overlap:
            score += len(cat_overlap) * 6

        # Synonym category / tag mappings (e.g. footwear -> shoes/sandals, audio -> earpods)
        if "footwear" in q and ("slip-ons" in p_cat or "footwear" in p_name):
            score += 18
        if "audio" in q and ("audio" in p_cat or "earpods" in p_name or "earbuds" in p_tags):
            score += 18
        if "leather" in q and ("leather" in p_cat or "leather" in p_desc or "leather" in p_tags):
            score += 18

        # Description / Tag overlap
        desc_words = set(re.findall(r'\b\w+\b', p_desc))
        tag_words = set(re.findall(r'\b\w+\b', p_tags))
        score += len(words.intersection(tag_words)) * 4
        score += len(words.intersection(desc_words)) * 2

        if score > 0:
            scored_products.append((score, p))

    # If specific products matched, sort and return top results
    if scored_products:
        scored_products.sort(key=lambda x: x[0], reverse=True)
        top_match = scored_products[0][1]
        intent_meta["target_product"] = top_match.name
        results = [serialize_product(p) for _, p in scored_products[:top_k]]
        return results, intent_meta

    # If no specific product matched, but general catalog inquiry detected ("what are available", "what can i buy", etc.)
    if is_general_catalog or "available" in q or "buy" in q or "have" in q or "products" in q or "items" in q:
        # Return all in-stock products
        in_stock_products = [p for p in products if p.stock_quantity > 0]
        results = [serialize_product(p) for p in in_stock_products[:top_k]]
        return results, intent_meta

    # Fallback: No matching product found in ShopSense
    return [], intent_meta


def serialize_product(p: Product) -> Dict[str, Any]:
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category or "General",
        "price": float(p.price),
        "stock_quantity": int(p.stock_quantity),
        "description": p.description or "Quality marketplace product",
        "tags": p.tags or "",
        "image_url": p.image_url or "",
        "vendor_id": p.vendor_id
    }


def generate_deterministic_answer(question: str, products: List[Dict[str, Any]], intent_meta: Dict[str, Any]) -> str:
    """
    Intelligent natural-language generator based on query intent and retrieved product context.
    """
    if intent_meta.get("intent") == "unrelated":
        return (
            "I'm here to assist you with the ShopSense store! I can help you find products, "
            "check prices, explore categories, check stock availability, or recommend items from our catalog. "
            "Please let me know what product or category you are looking for!"
        )

    if not products:
        return "I couldn't find a matching product in the available ShopSense catalog."

    q = question.lower()
    is_low_stock = intent_meta.get("is_low_stock", False)
    is_price_query = intent_meta.get("is_price_query", False)
    is_avail_query = intent_meta.get("is_avail_query", False)

    # 1. Low Stock Response
    if is_low_stock:
        low_items = [f"- **{p['name']}** — {p['stock_quantity']} units remaining (${p['price']:.2f})" for p in products if p['stock_quantity'] <= 20]
        if low_items:
            return "The following products are running low in stock:\n\n" + "\n".join(low_items) + "\n\nWe recommend purchasing or restocking soon before they sell out!"
        return "All matching products currently have healthy stock levels (>20 units)."

    # 2. Specific Product Query (1 or 2 products returned)
    if len(products) == 1 or intent_meta.get("target_product"):
        p = products[0]
        in_stock = p['stock_quantity'] > 0
        stock_status = f"{p['stock_quantity']} units in stock" if in_stock else "currently out of stock"

        # If user explicitly asked about price ("how much is...", "price of...")
        if is_price_query:
            return (
                f"The **{p['name']}** is priced at **${p['price']:.2f}** (Category: *{p['category']}*).\n\n"
                f"Currently, there are **{p['stock_quantity']} units** available in stock."
            )

        # If user explicitly asked about availability ("is the ... available?")
        if is_avail_query and any(w in q for w in ["is", "available", "how many"]):
            if in_stock:
                return (
                    f"Yes! The **{p['name']}** is currently available in stock.\n\n"
                    f"We have **{p['stock_quantity']} units** available at **${p['price']:.2f}** each "
                    f"(Category: *{p['category']}*)."
                )
            else:
                return f"Currently, the **{p['name']}** is out of stock in our store."

        # General product detail
        return (
            f"**{p['name']}** is available in the *{p['category']}* category for **${p['price']:.2f}**.\n\n"
            f"**Details:** {p['description']}\n"
            f"**Availability:** {stock_status}."
        )

    # 3. Category Response (all products share same category)
    category_set = set(p['category'] for p in products)
    if len(category_set) == 1:
        cat_name = list(category_set)[0]
        lines = [f"- **{p['name']}** — ${p['price']:.2f} ({p['stock_quantity']} in stock)\n  *{p['description']}*" for p in products]
        return f"Here are the available products in the **{cat_name}** category:\n\n" + "\n\n".join(lines)

    # 4. General Catalog / Product List Response
    lines = []
    for p in products:
        status_text = f"{p['stock_quantity']} in stock" if p['stock_quantity'] > 0 else "Out of stock"
        lines.append(f"- **{p['name']}** — ${p['price']:.2f} ({p['category']} | {status_text})")

    return (
        "Here are the products currently available in ShopSense:\n\n"
        + "\n".join(lines)
        + "\n\nFeel free to ask for more details or prices on any specific item!"
    )


def generate_rag_answer(question: str, products: List[Dict[str, Any]], intent_meta: Dict[str, Any]) -> str:
    """
    Generates an answer using LLM (Gemini) with retrieved product context.
    Falls back gracefully to deterministic synthesis if API key is not configured or fails.
    """
    if intent_meta.get("intent") == "unrelated":
        return (
            "I'm here to assist you with the ShopSense store! I can help you find products, "
            "check prices, explore categories, check stock availability, or recommend items from our catalog. "
            "Please let me know what product or category you are looking for!"
        )

    if not products:
        return "I couldn't find a matching product in the available ShopSense catalog."

    # Build structured context string from retrieved products
    context_blocks = []
    for p in products:
        status = f"{p['stock_quantity']} units available" if p['stock_quantity'] > 0 else "Out of stock"
        context_blocks.append(
            f"- Product: {p['name']}\n"
            f"  Category: {p['category']}\n"
            f"  Price: ${p['price']:.2f}\n"
            f"  Stock: {status}\n"
            f"  Description: {p['description']}\n"
            f"  Tags: {p['tags']}"
        )
    context_str = "\n\n".join(context_blocks)

    # Check for API Key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

            prompt = f"""You are the official ShopSense AI Shopping Assistant. Your role is to help customers learn about and find products in the ShopSense store.

STRICT INSTRUCTIONS:
1. Base your answer EXCLUSIVELY on the retrieved product context provided below.
2. Directly answer the customer's intent:
   - If they ask about price ("how much is...", "what is the price of..."), answer the price directly first.
   - If they ask about availability ("is ... available?", "how many in stock?"), confirm if it is in stock and state the count.
   - If they ask for available products, list the items concisely.
   - If they ask about low stock, identify the items with limited stock.
3. Clearly mention product names, prices ($), categories, and stock status.
4. Do NOT invent, assume, or hallucinate products, prices, or attributes not present in the context.
5. If the retrieved context does not contain what the customer is asking about, reply: "I couldn't find a matching product in the available ShopSense catalog."
6. Keep your response helpful, friendly, and concise.

Customer Question: {question}

Retrieved ShopSense Product Context:
{context_str}
"""
            response = llm.invoke(prompt)
            content = response.content.strip()
            if content:
                return content
        except Exception as e:
            logger.warning(f"Gemini LLM call failed or unavailable ({e}); utilizing deterministic RAG generator.")

    # Safe deterministic fallback
    return generate_deterministic_answer(question, products, intent_meta)


def ask_shopping_assistant(db: Session, question: str) -> Dict[str, Any]:
    """
    End-to-end RAG Shopping Assistant pipeline:
    1. Read-only retrieval of relevant products from PostgreSQL.
    2. Context injection and LLM / deterministic answer generation.
    3. Returns natural language answer + structured product list for UI cards.
    """
    clean_question = (question or "").strip()
    if not clean_question:
        return {
            "answer": "Please ask a question about available products, categories, or inventory!",
            "products": []
        }

    retrieved_products, intent_meta = retrieve_relevant_products(db, clean_question, top_k=6)
    answer = generate_rag_answer(clean_question, retrieved_products, intent_meta)

    return {
        "answer": answer,
        "products": retrieved_products
    }
