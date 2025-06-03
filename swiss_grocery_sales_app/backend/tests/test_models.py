import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

# It's often better to use a separate in-memory SQLite DB for such tests if models are simple,
# or mock the DB session if complex interactions are needed.
# For just instantiating models, we don't strictly need a session yet.
from app.models import Store, Promotion # Adjust import if your structure differs
from app.database import Base # To create tables in an in-memory DB for testing if needed

# Configure a separate in-memory SQLite database for model tests if you want to test session interactions.
# For now, these tests will just instantiate the models without committing to a DB.
# SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///:memory:"
# engine_test = create_engine(SQLALCHEMY_DATABASE_URL_TEST)
# SessionLocal_test = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# @pytest.fixture(scope="function")
# def db_session():
#     Base.metadata.create_all(bind=engine_test) # Create tables
#     db = SessionLocal_test()
#     try:
#         yield db
#     finally:
#         db.close()
#         Base.metadata.drop_all(bind=engine_test) # Drop tables after test


def test_create_store_instance():
    """Test creating an instance of the Store model."""
    store_data = {
        "name": "Test Migros",
        "address": "123 Test Street, Zurich",
        "latitude": 47.3769,
        "longitude": 8.5417,
        "chain_name": "Migros",
        # geom would be set by a transformation from lat/lon in a real scenario
        # For direct model instantiation, we might omit it or mock GeoAlchemy2 types if they cause issues without a DB
    }
    store = Store(**store_data)

    assert store.name == store_data["name"]
    assert store.address == store_data["address"]
    assert store.latitude == store_data["latitude"]
    assert store.longitude == store_data["longitude"]
    assert store.chain_name == store_data["chain_name"]
    # assert store.id is None # ID is None until committed to DB and auto-incremented

def test_create_promotion_instance():
    """Test creating an instance of the Promotion model."""
    promotion_data = {
        "store_id": 1, # Assuming a store with ID 1 exists (for relationship purposes)
        "product_name": "Test Product",
        "sale_price": 9.95,
        "original_price": 12.50,
        "valid_until": date(2024, 12, 31),
        "description": "A great test product on sale.",
        "image_url": "http://example.com/image.png",
        # last_updated would be set by the DB or application logic
    }
    promotion = Promotion(**promotion_data)

    assert promotion.store_id == promotion_data["store_id"]
    assert promotion.product_name == promotion_data["product_name"]
    assert promotion.sale_price == promotion_data["sale_price"]
    assert promotion.original_price == promotion_data["original_price"]
    assert promotion.valid_until == promotion_data["valid_until"]
    # assert promotion.id is None # ID is None until committed

def test_store_promotion_relationship_instantiation():
    """Test creating Store and Promotion and linking them (in memory)."""
    store = Store(
        name="Test Coop",
        address="456 Sample Avenue, Geneva",
        latitude=46.2044,
        longitude=6.1432,
        chain_name="Coop"
    )

    promotion = Promotion(
        product_name="Super Sale Item",
        sale_price=5.00,
        # store_id would be set if adding to a session and committing.
        # For in-memory, we can assign the object.
    )

    # Append to the relationship list (this is how SQLAlchemy relationships work)
    store.promotions.append(promotion)
    # promotion.store = store # This also works and sets up both sides

    assert promotion in store.promotions
    assert promotion.store == store # This assertion works after linking
