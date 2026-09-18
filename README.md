# ShopSense — Multi-Vendor E-Commerce Analytics Platform

An end-to-end e-commerce analytics web application that helps vendors manage products, monitor business performance, and make data-informed inventory decisions.

Built as part of the **Infosys Springboard Internship Program**.

---

## 📌 Overview

**ShopSense** is a multi-vendor e-commerce analytics platform designed to simplify vendor operations through inventory management, business insights, demand forecasting, and customer review analysis.

The platform provides a centralized interface where vendors can manage their products, track sales performance, and use analytical tools to support inventory planning.

### Key Objectives

* Simplify vendor and administrator access through role-based authentication.
* Provide real-time business metrics through an interactive dashboard.
* Enable efficient product inventory management.
* Support inventory planning through demand forecasting.
* Analyze customer feedback using sentiment classification.

---

## 🏗️ Architecture & Technology Stack

| Layer                | Technology                                |
| -------------------- | ----------------------------------------- |
| Backend Framework    | FastAPI                                   |
| Programming Language | Python                                    |
| Database             | PostgreSQL with automatic SQLite fallback |
| Database ORM         | SQLAlchemy                                |
| Data Validation      | Pydantic v2                               |
| Frontend             | HTML5, CSS3, JavaScript (ES6+)            |
| API Architecture     | REST APIs                                 |
| Predictive Analytics | ARIMA Demand Forecasting                  |
| Containerization     | Docker                                    |

### Application Architecture

```text
                   ┌─────────────────────────┐
                   │       ShopSense         │
                   │  Multi-Vendor Platform  │
                   └────────────┬────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
   ┌──────────▼──────────┐             ┌──────────▼──────────┐
   │    Frontend UI      │             │    FastAPI Backend  │
   │ HTML • CSS • JS     │◄───────────►│     REST APIs       │
   └─────────────────────┘             └──────────┬──────────┘
                                                   │
                                    ┌──────────────┴──────────────┐
                                    │                             │
                         ┌──────────▼──────────┐     ┌──────────▼──────────┐
                         │   SQLAlchemy ORM    │     │ Analytics & Forecast│
                         │  Database Access    │     │  ARIMA • Sentiment  │
                         └──────────┬──────────┘     └─────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │ PostgreSQL / SQLite │
                         └─────────────────────┘
```

---

## 📁 Project Structure

```text
shopsense/
├── database.py              # Database engine and configuration
├── main.py                  # FastAPI application entry point
├── models.py                # SQLAlchemy database models
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image configuration
│
├── crud/                    # Database access layer
│   ├── vendor.py
│   ├── admin.py
│   ├── product.py
│   └── analytics.py
│
├── routers/                 # REST API route controllers
│   ├── vendor.py
│   ├── admin.py
│   ├── product.py
│   └── analytics.py
│
├── schemas/                 # Pydantic validation schemas
│   ├── vendor.py
│   ├── admin.py
│   ├── product.py
│   └── analytics.py
│
└── frontend/                # Frontend web application
    ├── login.html
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── api.js
    │   └── app.js
    └── vendor/
        └── dashboard.html
```

### Backend Layer Responsibilities

| Module        | Responsibility                                       |
| ------------- | ---------------------------------------------------- |
| `main.py`     | Starts the FastAPI application and configures routes |
| `database.py` | Establishes and manages database connectivity        |
| `models.py`   | Defines database entities and relationships          |
| `crud/`       | Handles database operations                          |
| `routers/`    | Defines API endpoints and request handling           |
| `schemas/`    | Validates and structures API data                    |

---

## ✨ Core Features

### 1. Authentication & Authorization

* Dual-role sign-in interface for **Vendors** and **Admins**.
* Vendor registration through a registration modal.
* Role-based access to platform functionality.

### 2. Vendor Analytics Dashboard

The vendor dashboard provides an overview of business performance through key metrics:

* Total Sales
* Sales Revenue
* Total Transactions
* Products Listed

These metrics help vendors monitor their business activity from a centralized dashboard.

### 3. Product Inventory Management

Vendors can manage their product catalog through CRUD operations:

* Create new products.
* View existing products.
* Update product information.
* Delete products.
* Add product image URLs.
* Classify products by category.
* Organize products using tags.

### 4. ARIMA Demand Forecasting

ShopSense includes an ARIMA-based time-series forecasting feature for inventory planning.

**Purpose:**

Analyze historical inventory or sales data to generate demand forecasts that can support short-term planning.

**Forecasting horizon:** 7 days.

> Forecast results are intended to support inventory decisions and should be interpreted as estimates rather than guaranteed future demand.

### 5. AI Sentiment Review Simulation

The platform includes a simulated AI-based sentiment analysis feature for customer reviews.

It analyzes:

* Customer ratings.
* Written customer feedback.
* Sentiment classification.
* AI-generated review summaries.

The feature is designed to help vendors understand customer feedback and identify general sentiment trends.

---

## 🚀 Running the Application

### Prerequisites

Make sure the following are installed:

* Python 3.x
* pip
* Git
* Docker *(optional, for containerized execution)*

### Option 1: Run Using a Local Python Environment

**1. Clone the repository**

```bash
git clone https://github.com/Ananya1315/TeamC-Shopsense.git
cd TeamC-Shopsense/shopsense
```

**2. Create a virtual environment**

Windows:

```bash
python -m venv venv
```

**3. Activate the virtual environment**

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Start the FastAPI server**

```bash
python -m uvicorn main:app --reload --port 8000
```

**6. Open the application**

| Resource                  | URL                                                  |
| ------------------------- | ---------------------------------------------------- |
| Login Page                | http://localhost:8000/frontend/login.html            |
| Vendor Dashboard          | http://localhost:8000/frontend/vendor/dashboard.html |
| Swagger API Documentation | http://localhost:8000/docs                           |

### Option 2: Run Using Docker

**1. Build the Docker image**

```bash
docker build -t shopsense .
```

**2. Start the container**

```bash
docker run -p 8000:8000 shopsense
```

**3. Access the application**

Open the login page:

```text
http://localhost:8000/frontend/login.html
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

> **Note:** Database configuration, environment variables, and any required initialization steps should be completed according to the project's implementation.

---

## 📚 API Documentation

ShopSense uses FastAPI to provide interactive API documentation.

Once the application is running, access:

**Swagger UI:** http://localhost:8000/docs

The documentation provides an interface for exploring and testing the available API endpoints.

---

## 🗄️ Database

ShopSense uses SQLAlchemy as its database ORM.

* **PostgreSQL:** Supported as the primary database option.
* **SQLite:** Available as a fallback database for local development.

The database models include entities such as:

* Vendor
* Admin
* Product
* Transaction
* Review

The actual database configuration is managed through the application's database setup.

---

## 🐳 Containerization

The application includes a `Dockerfile` for packaging and running ShopSense in a containerized environment.

Docker helps provide a consistent application environment and simplifies application setup across different systems.

---

## 🎯 Project Goals

ShopSense aims to combine e-commerce operations with analytics capabilities to help vendors:

* Manage their product inventory efficiently.
* Monitor sales and transaction activity.
* Understand customer feedback.
* Plan inventory using demand forecasts.
* Access business information through a centralized platform.

---

## 👥 Project Information

| Detail           | Information                                |
| ---------------- | ------------------------------------------ |
| Project          | ShopSense                                  |
| Type             | Multi-Vendor E-Commerce Analytics Platform |
| Program          | Infosys Springboard Internship             |
| Application      | Web Application                            |
| Backend          | FastAPI                                    |
| Frontend         | HTML, CSS, JavaScript                      |
| Database         | PostgreSQL / SQLite                        |
| Containerization | Docker                                     |

---

## 📄 License

This project was developed as part of the Infosys Springboard Internship Program.
