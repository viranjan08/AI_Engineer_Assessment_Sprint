import duckdb
import os
import pandas as pd
import re

DB_PATH = "data/tickets.duckdb"

def initialize_database():
    """Initializes the DuckDB database file."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with duckdb.connect(DB_PATH) as conn:
        # We can run any initial setup queries here
        pass

def get_connection():
    return duckdb.connect(DB_PATH)

def execute_read_only_query(query: str):
    """Executes a query ensuring no modifications are made."""
    if ';' in query:
        raise ValueError("Semicolons (;) are not allowed for security reasons to prevent SQL injection.")
        
    # Basic SQL injection/modification prevention at the application level
    forbidden_phrases = ['DROP TABLE', 'DELETE FROM', 'UPDATE ', 'INSERT INTO', 'ALTER TABLE', 'CREATE TABLE', 'TRUNCATE ']
    upper_query = query.upper()
    
    for phrase in forbidden_phrases:
        if phrase in upper_query:
            raise ValueError(f"Only read operations (SELECT) are allowed. Blocked by phrase: '{phrase}'")
    
    with duckdb.connect(DB_PATH) as conn:
        return conn.execute(query).fetchdf()

def load_tickets_from_dataframe(df: pd.DataFrame):
    """Loads a Pandas DataFrame into the tickets table."""
    with duckdb.connect(DB_PATH) as conn:
        conn.register('temp_df', df)
        conn.execute("CREATE OR REPLACE TABLE tickets AS SELECT * FROM temp_df")

def get_schema():
    """Returns the schema of the tickets table."""
    with duckdb.connect(DB_PATH) as conn:
        schema = conn.execute("DESCRIBE tickets").fetchdf()
        return schema
