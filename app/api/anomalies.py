from fastapi import APIRouter
from app.services.anomaly_service import detect_anomalies

router = APIRouter()

@router.get("/anomalies", tags=["Anomalies"])
def get_anomalies():
    results = detect_anomalies()
    return {
        "success": True,
        "count": len(results) if isinstance(results, list) else 0,
        "anomalies": results
    }
