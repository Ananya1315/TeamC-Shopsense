# ShopSense: Multi-Vendor E-Commerce Analytics Platform

ShopSense is an end-to-end multi-vendor e-commerce analytics web application built for the Infosys Springboard internship program.

## Architecture & Technology Stack
- **Backend Framework**: FastAPI (Python)
- **Database ORM**: SQLAlchemy with PostgreSQL & automatic SQLite fallback
- **Data Schemas**: Pydantic v2
- **Frontend UI**: Responsive SPA built with Vanilla HTML5, CSS3, and JavaScript (ES6+)
- **Containerization**: Docker

## Folder Structure
```
shopsense/
├── database.py       # DB connection engine (PostgreSQL + SQLite fallback)
├── main.py           # FastAPI application entrypoint & static routes
├── models.py         # SQLAlchemy ORM models (Vendor, Admin, Product, Transaction, Review)
├── requirements.txt  # Dependency list
├── Dockerfile        # Container build instructions
├── crud/             # Database access layer
│   ├── vendor.py
│   ├── admin.py
│   ├── product.py
│   └── analytics.py
├── routers/          # REST API Controllers
│   ├── vendor.py
│   ├── admin.py
│   ├── product.py
│   └── analytics.py
├── schemas/          # Pydantic data validation models
│   ├── vendor.py
│   ├── admin.py
│   ├── product.py
│   └── analytics.py
└── frontend/         # Frontend Web Application
    ├── login.html
    ├── css/style.css
    ├── js/api.js
    ├── js/app.js
    └── vendor/
        └── dashboard.html
```

## Running the Application

### Option 1: Local Python Environment
1. Ensure virtual environment is activated.
2. Run the server:
```bash
python -m uvicorn main:app --reload --port 8000
```
3. Open your browser to:
   - **Login Page**: `http://localhost:8000/frontend/login.html`
   - **Vendor Dashboard**: `http://localhost:8000/frontend/vendor/dashboard.html`
   - **API Documentation (Swagger UI)**: `http://localhost:8000/docs`

### Option 2: Docker Container
```bash
docker build -t shopsense .
docker run -p 8000:8000 shopsense
```

## Core Features
1. **Authentication & Authorization**: Dual-role sign-in interface for Vendors and Admins with registration modal.
2. **Vendor Dashboard**: Real-time business metrics tracking Total Sales, Sale Revenue, Total Transactions, and Products Listed.
3. **Product Inventory Management**: Full Product CRUD with image URL support, category classification, and tags.
4. **ARIMA Demand Forecasting**: Time-series predictive inventory forecasting for 7-day inventory planning.
5. **AI Sentiment Review Simulation**: Intelligent sentiment classifier analyzing customer ratings and textual feedback with AI summaries.
