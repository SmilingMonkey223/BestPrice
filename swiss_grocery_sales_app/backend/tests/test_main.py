from fastapi.testclient import TestClient
from app.main import app # Assuming app.main is accessible

client = TestClient(app)

# Test for successful geocoding
def test_geocode_address_success(mocker):
    # Mock the fetch_coordinates_from_geo_admin function
    mock_coords = (46.947975, 7.447447) # Example coordinates for Bern
    mocked_fetch = mocker.patch(
        'app.main.fetch_coordinates_from_geo_admin',
        return_value=mock_coords
    )

    response = client.post("/api/v1/geocode", json={"address": "Bundesplatz 1, 3011 Bern"})

    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == mock_coords[0]
    assert data["longitude"] == mock_coords[1]
    # Verify the mock was called correctly (optional, but good practice)
    mocked_fetch.assert_called_once_with("Bundesplatz 1, 3011 Bern")

# Test for when the address is not found by GeoAdmin (returns None)
def test_geocode_address_not_found(mocker):
    mocked_fetch = mocker.patch(
        'app.main.fetch_coordinates_from_geo_admin',
        return_value=None # Simulate address not found
    )

    test_address = "NonExistent Address 123, FantasyLand"
    response = client.post("/api/v1/geocode", json={"address": test_address})

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Address not found or could not be geocoded: {test_address}"
    mocked_fetch.assert_called_once_with(test_address)

# Test for FastAPI's validation error if 'address' field is missing
def test_geocode_address_missing_address_payload():
    # No mocking needed here as it's a request validation handled by FastAPI
    response = client.post("/api/v1/geocode", json={}) # Missing 'address' field
    assert response.status_code == 422 # FastAPI's default for validation errors
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["loc"] == ["body", "address"]
