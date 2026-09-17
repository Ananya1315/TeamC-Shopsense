from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import schemas.ai as schema
import crud.ai_assistant as crud_assistant
import crud.ai_analyst as crud_analyst

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/assistant", response_model=schema.AssistantResponse)
def ask_shopping_assistant(req: schema.AssistantRequest, db: Session = Depends(get_db)):
    """
    RAG-based AI Shopping Assistant endpoint.
    Strictly read-only: retrieves matching product context from PostgreSQL and generates grounded responses.
    """
    result = crud_assistant.ask_shopping_assistant(db, req.question)
    return schema.AssistantResponse(
        answer=result["answer"],
        products=result["products"]
    )

@router.post("/analyst", response_model=schema.AnalystResponse)
def ask_data_analyst(req: schema.AnalystRequest, db: Session = Depends(get_db)):
    """
    Hybrid AI Data Analyst endpoint:
    Intelligently routes questions across ShopSense internal PostgreSQL database,
    external real-world web search grounding, and hybrid combinations.
    """
    result = crud_analyst.ask_data_analyst(
        db=db,
        question=req.question,
        role=req.role or "Vendor",
        vendor_id=req.vendor_id
    )
    return schema.AnalystResponse(
        answer=result["answer"],
        data=result.get("data", []),
        sql_executed=result.get("sql_executed"),
        source=result.get("source", "ShopSense business data"),
        citations=result.get("citations", []),
        intent=result.get("intent")
    )

