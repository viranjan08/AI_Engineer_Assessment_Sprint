from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import ask_question
from app.models.schemas import QueryResponse

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/query", response_model=QueryResponse, tags=["AI Query"])
def handle_query(request: QueryRequest):
    return ask_question(request.question)
