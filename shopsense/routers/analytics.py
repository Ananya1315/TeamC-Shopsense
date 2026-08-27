from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import crud.analytics as crud
import schemas.analytics as schema
from database import SessionLocal

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard", response_model=schema.DashboardMetrics)
def get_dashboard_metrics(
    vendor_id: Optional[int] = Query(1),
    db: Session = Depends(get_db)
):
    return crud.get_vendor_dashboard_metrics(db, vendor_id or 1)

@router.get("/low-stock", response_model=List[schema.LowStockAlert])
def get_low_stock_alerts(
    vendor_id: Optional[int] = Query(1),
    threshold: int = Query(10),
    db: Session = Depends(get_db)
):
    return crud.get_low_stock_alerts(db, vendor_id or 1, threshold)

@router.post("/forecast", response_model=schema.ForecastResponse)
def get_arima_forecast(
    req: schema.ForecastRequest,
    db: Session = Depends(get_db)
):
    return crud.run_arima_forecast(db, req.product_id)

@router.post("/sentiment", response_model=schema.ReviewSentimentResponse)
def analyze_review_sentiment(
    req: schema.ReviewSentimentRequest,
    db: Session = Depends(get_db)
):
    return crud.analyze_review_sentiment(db, req.product_id, req.rating, req.review_text)

@router.get("/customer-segmentation", response_model=schema.CustomerAnalyticsResponse)
def get_customer_segmentation(
    vendor_id: int = Query(...),
    db: Session = Depends(get_db)
):
    return crud.get_customer_segmentation(db, vendor_id)

@router.get("/recommendations", response_model=schema.RecommendationResponse)
def get_recommendations(
    vendor_id: int = Query(...),
    db: Session = Depends(get_db)
):
    return crud.get_rule_based_recommendations(db, vendor_id)

@router.post("/seed", response_model=schema.SeedDataResponse)
def seed_historical_data(
    vendor_id: int = Query(...),
    db: Session = Depends(get_db)
):
    return crud.seed_historical_data(db, vendor_id)
