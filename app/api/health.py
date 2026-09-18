from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "message": "System is running"}
