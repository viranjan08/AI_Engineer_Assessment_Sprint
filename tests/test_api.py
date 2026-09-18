from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "System is running"}

def test_anomalies_endpoint():
    response = client.get("/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "count" in data
    assert "anomalies" in data
