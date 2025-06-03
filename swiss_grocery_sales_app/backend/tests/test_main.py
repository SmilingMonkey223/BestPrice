from fastapi.testclient import TestClient
from app.main import app # Main FastAPI application
from app import schemas, models # To help construct Pydantic models and mock returns
# from app import crud # For mocker.patch path if needed, already imported by app.main
from unittest.mock import ANY # For db session argument matching

client = TestClient(app)

# --- Existing Geocoding Tests (Keep As Is) ---
def test_geocode_address_success(mocker):
    mock_coords = (46.947975, 7.447447)
    # Path to fetch_coordinates_from_geo_admin is app.main because it's imported there
    mocked_fetch = mocker.patch('app.main.fetch_coordinates_from_geo_admin', return_value=mock_coords)
    response = client.post("/api/v1/geocode", json={"address": "Bundesplatz 1, 3011 Bern"})
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == mock_coords[0]
    assert data["longitude"] == mock_coords[1]
    # Correct way to access the mock for assertion if it's part of app.main's namespace
    mocked_fetch.assert_called_once_with("Bundesplatz 1, 3011 Bern")


def test_geocode_address_not_found(mocker):
    mocked_fetch = mocker.patch('app.main.fetch_coordinates_from_geo_admin', return_value=None)
    test_address = "NonExistent Address 123, FantasyLand"
    response = client.post("/api/v1/geocode", json={"address": test_address})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Address not found or could not be geocoded: {test_address}"
    mocked_fetch.assert_called_once_with(test_address)

def test_geocode_address_missing_address_payload():
    response = client.post("/api/v1/geocode", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["loc"] == ["body", "address"]

# --- Existing Store Endpoint Tests (Keep As Is) ---
def test_create_new_store_success(mocker):
    store_payload = { "name": "Test Store Migros", "address": "123 Test St, Zurich", "latitude": 47.3769, "longitude": 8.5417, "chain_name": "Migros" }
    # Mocked return value from crud.create_store
    mock_created_store_db = models.Store(
        id=1,  # Assume DB assigns an ID
        name=store_payload["name"],
        address=store_payload["address"],
        latitude=store_payload["latitude"],
        longitude=store_payload["longitude"],
        chain_name=store_payload["chain_name"],
        geom=f"POINT({store_payload['longitude']} {store_payload['latitude']})"
    )
    mock_crud_create_store = mocker.patch('app.crud.create_store', return_value=mock_created_store_db)
    response = client.post("/api/v1/stores", json=store_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == store_payload["name"]
    assert data["address"] == store_payload["address"]
    assert data["latitude"] == store_payload["latitude"]
    assert data["longitude"] == store_payload["longitude"]
    assert data["chain_name"] == store_payload["chain_name"]
    assert data["id"] == mock_created_store_db.id
    assert "promotions" in data
    called_args, called_kwargs = mock_crud_create_store.call_args
    assert called_kwargs['store'].name == store_payload['name']

def test_create_new_store_invalid_payload():
    response = client.post("/api/v1/stores", json={"chain_name": "Migros"}) # Missing required fields
    assert response.status_code == 422

def test_read_store_success(mocker):
    store_id = 1
    mock_db_store = models.Store(id=store_id, name="Test Store Coop", address="456 Example Ave, Bern", latitude=46.9480, longitude=7.4474, chain_name="Coop", geom="POINT(7.4474 46.9480)")
    mock_crud_get_store = mocker.patch('app.crud.get_store', return_value=mock_db_store)
    response = client.get(f"/api/v1/stores/{store_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_db_store.id
    assert data["name"] == mock_db_store.name
    assert data["address"] == mock_db_store.address
    mock_crud_get_store.assert_called_once_with(db=ANY, store_id=store_id)

def test_read_store_not_found(mocker):
    store_id = 999
    mocker.patch('app.crud.get_store', return_value=None)
    response = client.get(f"/api/v1/stores/{store_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Store with ID {store_id} not found"

# --- New Geospatial Store Search Endpoint Tests ---

def test_read_stores_nearby_success(mocker):
    mock_stores_db = [
        models.Store(id=1, name="Nearby Store 1", address="1km Away", latitude=47.0, longitude=8.0, chain_name="Coop", geom="POINT(8.0 47.0)"),
        models.Store(id=2, name="Nearby Store 2", address="2km Away", latitude=47.01, longitude=8.01, chain_name="Migros", geom="POINT(8.01 47.01)")
    ]
    mock_crud_get_stores_nearby = mocker.patch('app.crud.get_stores_within_radius', return_value=mock_stores_db)

    params = {"latitude": 47.0, "longitude": 8.0, "radius_km": 5, "skip": 0, "limit": 10}
    response = client.get("/api/v1/stores", params=params)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(mock_stores_db)
    assert data[0]["name"] == mock_stores_db[0].name
    assert data[1]["id"] == mock_stores_db[1].id

    mock_crud_get_stores_nearby.assert_called_once_with(
        db=ANY,
        latitude=params["latitude"],
        longitude=params["longitude"],
        radius_km=params["radius_km"],
        skip=params["skip"],
        limit=params["limit"]
    )

def test_read_stores_nearby_missing_manda_params():
    # Missing latitude
    response_no_lat = client.get("/api/v1/stores", params={"longitude": 8.0, "radius_km": 5})
    assert response_no_lat.status_code == 422

    # Missing longitude
    response_no_lon = client.get("/api/v1/stores", params={"latitude": 47.0, "radius_km": 5})
    assert response_no_lon.status_code == 422

def test_read_stores_nearby_invalid_radius():
    # Radius too small (gt=0 validation)
    response_small_radius = client.get("/api/v1/stores", params={"latitude": 47.0, "longitude": 8.0, "radius_km": 0})
    assert response_small_radius.status_code == 422

    # Radius too large (le=50 validation)
    response_large_radius = client.get("/api/v1/stores", params={"latitude": 47.0, "longitude": 8.0, "radius_km": 100})
    assert response_large_radius.status_code == 422

def test_read_stores_nearby_invalid_pagination():
    # Skip less than 0
    response_invalid_skip = client.get("/api/v1/stores", params={"latitude": 47.0, "longitude": 8.0, "radius_km": 5, "skip": -1})
    assert response_invalid_skip.status_code == 422

    # Limit less than 1
    response_invalid_limit_small = client.get("/api/v1/stores", params={"latitude": 47.0, "longitude": 8.0, "radius_km": 5, "limit": 0})
    assert response_invalid_limit_small.status_code == 422

    # Limit greater than 200
    response_invalid_limit_large = client.get("/api/v1/stores", params={"latitude": 47.0, "longitude": 8.0, "radius_km": 5, "limit": 201})
    assert response_invalid_limit_large.status_code == 422


def test_read_stores_nearby_empty_result(mocker):
    mock_crud_get_stores_nearby = mocker.patch('app.crud.get_stores_within_radius', return_value=[]) # Return empty list

    params = {"latitude": 47.0, "longitude": 8.0, "radius_km": 1} # A query that might yield no results
    response = client.get("/api/v1/stores", params=params)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    mock_crud_get_stores_nearby.assert_called_once()
