from fastapi import APIRouter, UploadFile, File
import shutil
import os
from app.services.ingestion_service import ingest_csv

router = APIRouter()

@router.post("/upload", tags=["Data"])
async def upload_dataset(file: UploadFile = File(...)):
    temp_path = f"data/{file.filename}"
    os.makedirs("data", exist_ok=True)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        rows_ingested = ingest_csv(temp_path)
        return {"success": True, "message": f"Successfully ingested {rows_ingested} rows."}
    except Exception as e:
        return {"success": False, "error": str(e)}
