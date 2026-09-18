from fastapi import FastAPI
from app.api import query, anomalies, health, upload
from app.services.ingestion_service import ingest_csv
import os

app = FastAPI(title="AI Support Ticket Analytics System")

@app.on_event("startup")
def startup_event():
    # Automatically ingest the default CSV if it exists
    csv_path = "support_tickets.csv"
    if os.path.exists(csv_path):
        try:
            ingest_csv(csv_path)
            print(f"Successfully ingested {csv_path} into DuckDB.")
        except Exception as e:
            print(f"Failed to ingest CSV on startup: {e}")

# Include routers
app.include_router(health.router)
app.include_router(query.router)
app.include_router(anomalies.router)
app.include_router(upload.router)
