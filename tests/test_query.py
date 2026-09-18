from app.services.llm_service import build_sql_from_intent
from app.models.schemas import QueryIntent

def test_build_sql_count():
    intent = QueryIntent(intent="count", filters={"status": "Open"})
    sql = build_sql_from_intent(intent)
    assert "SELECT COUNT(*) as result FROM tickets" in sql
    assert "status = 'Open'" in sql

def test_build_sql_anomalies():
    intent = QueryIntent(intent="filter", timeframe="this_week", filters={"resolution_time_hrs": ">48"})
    sql = build_sql_from_intent(intent)
    assert "INTERVAL 7 DAY" in sql
    assert "resolution_time_hrs > 48" in sql
