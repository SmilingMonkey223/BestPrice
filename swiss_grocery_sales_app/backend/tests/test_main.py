from fastapi.testclient import TestClient
# Adjust the import path based on your project structure.
# Assuming 'app.main' is accessible from the 'backend' directory where pytest will be run.
from app.main import app

client = TestClient(app)

def test_geocode_address_mock():
    response = client.post("/api/v1/geocode", json={"address": "Teststrasse 1, 8000 Zurich"})
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 47.3769
    assert data["longitude"] == 8.5417

def test_geocode_address_missing_address():
    response = client.post("/api/v1/geocode", json={}) # Missing 'address' field
    assert response.status_code == 422 # FastAPI's default for validation errors
