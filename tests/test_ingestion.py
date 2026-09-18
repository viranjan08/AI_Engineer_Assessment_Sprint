from app.services.ingestion_service import ingest_csv
from app.database.duckdb_manager import execute_read_only_query
import os

def test_ingestion():
    if os.path.exists("support_tickets.csv"):
        ingest_csv("support_tickets.csv")
        df = execute_read_only_query("SELECT COUNT(*) as count FROM tickets")
        assert df.iloc[0]['count'] > 0
