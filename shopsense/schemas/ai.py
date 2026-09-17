from pydantic import BaseModel
from typing import List, Optional

class AssistantRequest(BaseModel):
    question: str

class AssistantResponse(BaseModel):
    answer: str
    products: Optional[List[dict]] = None

class AnalystRequest(BaseModel):
    question: str
    vendor_id: Optional[int] = None
    role: Optional[str] = "Vendor"

class AnalystResponse(BaseModel):
    answer: str
    data: Optional[List[dict]] = None
    sql_executed: Optional[str] = None
    source: Optional[str] = "ShopSense business data"
    citations: Optional[List[dict]] = None
    intent: Optional[str] = None
