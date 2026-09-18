import pandas as pd
import os
from app.database.duckdb_manager import load_tickets_from_dataframe

def ingest_csv(file_path: str):
    """Reads the CSV, validates, calculates derived fields, and loads into DuckDB."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset {file_path} not found.")

    df = pd.read_csv(file_path)
    
    # 1. Convert created_at to datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    
    # 2. Calculate derived fields
    df['is_resolved'] = df['status'] == 'Resolved'
    df['is_high_priority'] = df['priority'].isin(['High', 'Critical'])
    
    # Calculate ticket age (using max created_at as 'current time' for static datasets)
    current_time = df['created_at'].max()
    df['ticket_age_hours'] = (current_time - df['created_at']).dt.total_seconds() / 3600.0
    
    df['is_over_24h'] = df['ticket_age_hours'] > 24
    
    # 3. Load into DuckDB
    load_tickets_from_dataframe(df)
    
    return len(df)
