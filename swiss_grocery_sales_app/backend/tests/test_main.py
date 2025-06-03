from fastapi.testclient import TestClient
from app.main import app # Main FastAPI application
from app import schemas # To help construct expected Pydantic models
from app import models # To help construct mock return values from crud
from datetime import datetime # For potential date comparisons

# If crud functions are directly in app.crud
# from app import crud # This might be needed for mocker.patch path

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

# --- New Store Endpoint Tests ---

def test_create_new_store_success(mocker):
    store_payload = {
        "name": "Test Store Migros",
        "address": "123 Test St, Zurich",
        "latitude": 47.3769,
        "longitude": 8.5417,
        "chain_name": "Migros"
    }

    # Mocked return value from crud.create_store
    # This should be an instance of models.Store
    mock_created_store_db = models.Store(
        id=1,  # Assume DB assigns an ID
        name=store_payload["name"],
        address=store_payload["address"],
        latitude=store_payload["latitude"],
        longitude=store_payload["longitude"],
        chain_name=store_payload["chain_name"],
        geom=f"POINT({store_payload['longitude']} {store_payload['latitude']})"
        # promotions list would be empty by default for a new store
    )

    # Patch the crud.create_store function. Path is 'app.crud.create_store'
    # because create_new_store in main.py calls crud.create_store
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
    assert "promotions" in data # Should be present, likely empty list

    # Verify that crud.create_store was called
    # The first argument to crud.create_store is the db session, which we can't easily check here without more complex mocking.
    # So we check that it was called, and can inspect the 'store' argument.
    # For a more precise check of the `store` argument, ensure it matches `schemas.StoreCreate(**store_payload)`
    called_args, called_kwargs = mock_crud_create_store.call_args
    assert called_kwargs['store'].name == store_payload['name'] # Check one field of the StoreCreate object passed


def test_create_new_store_invalid_payload():
    invalid_payload = { # Missing 'name', 'address', 'latitude', 'longitude'
        "chain_name": "Migros"
    }
    response = client.post("/api/v1/stores", json=invalid_payload)
    assert response.status_code == 422 # Unprocessable Entity


def test_read_store_success(mocker):
    store_id = 1
    # Mocked return value from crud.get_store (models.Store instance)
    mock_db_store = models.Store(
        id=store_id,
        name="Test Store Coop",
        address="456 Example Ave, Bern",
        latitude=46.9480, # Corrected: no quote before latitude
        longitude=7.4474, # Corrected: no quote before longitude
        chain_name="Coop",
        geom="POINT(7.4474 46.9480)"
        # promotions list would be empty or populated depending on what crud.get_store returns
    )
    # Example of adding a promotion to the mock store if needed for testing StoreRead with promotions
    # mock_db_store.promotions = [models.Promotion(id=1, store_id=store_id, product_name="Test Promo", sale_price=10.0, last_updated=datetime.utcnow())]

    mock_crud_get_store = mocker.patch('app.crud.get_store', return_value=mock_db_store)

    response = client.get(f"/api/v1/stores/{store_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_db_store.id
    assert data["name"] == mock_db_store.name
    assert data["address"] == mock_db_store.address
    # assert len(data["promotions"]) == len(mock_db_store.promotions) # If promotions are mocked

    mock_crud_get_store.assert_called_once_with(db=mocker.ANY, store_id=store_id)


def test_read_store_not_found(mocker):
    store_id = 999 # An ID that presumably doesn't exist
    mocker.patch('app.crud.get_store', return_value=None) # Simulate store not found

    response = client.get(f"/api/v1/stores/{store_id}")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Store with ID {store_id} not found"
