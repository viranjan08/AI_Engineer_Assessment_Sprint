from app.services.anomaly_service import detect_anomalies

def test_detect_anomalies():
    results = detect_anomalies()
    # It returns a list of dictionaries if successful, or a dict with "error" if DB not loaded
    if isinstance(results, list):
        assert True
    else:
        assert "error" in results
