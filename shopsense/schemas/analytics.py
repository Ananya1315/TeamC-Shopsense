from pydantic import BaseModel
from typing import List, Optional

class DashboardMetrics(BaseModel):
    total_sales: int
    sale_revenue: float
    total_transactions: int
    products_listed: int

class LowStockAlert(BaseModel):
    id: int
    name: str
    stock_quantity: int
    category: str

class ForecastRequest(BaseModel):
    product_id: int

class ForecastPoint(BaseModel):
    day: str
    predicted_sales: int

class ForecastResponse(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    forecast: List[ForecastPoint]
    recommendation: str

class ReviewSentimentRequest(BaseModel):
    product_id: int
    rating: int
    review_text: str

class ReviewSentimentResponse(BaseModel):
    product_id: int
    rating: int
    sentiment: str
    confidence_score: float
    summary: str
    top_pros: Optional[List[str]] = []
    top_cons: Optional[List[str]] = []

class CustomerSegment(BaseModel):
    segment_name: str
    customer_count: int
    total_spending: float
    description: str

class CustomerAnalyticsResponse(BaseModel):
    vendor_id: int
    segments: List[CustomerSegment]

class ProductRecommendation(BaseModel):
    product_id: int
    product_name: str
    category: str
    sales_quantity: int
    reason: str

class RecommendationResponse(BaseModel):
    vendor_id: int
    recommendations: List[ProductRecommendation]

class SeedDataResponse(BaseModel):
    message: str
    customers_added: int
    transactions_added: int
