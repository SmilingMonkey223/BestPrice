from sqlalchemy.orm import Session
from typing import Optional

from . import models
from . import schemas

# For creating WKT Point for GeoAlchemy2
# from geoalchemy2.shape import from_shape # If using shapely
# from shapely.geometry import Point # If using shapely

def get_store(db: Session, store_id: int) -> Optional[models.Store]:
    """
    Retrieves a store by its ID.
    """
    return db.query(models.Store).filter(models.Store.id == store_id).first()

def create_store(db: Session, store: schemas.StoreCreate) -> models.Store:
    """
    Creates a new store in the database.
    The 'geom' field is populated from latitude and longitude.
    """

    # Construct WKT for the POINT geometry. SRID is handled by the column definition.
    # Ensure longitude comes first, then latitude in POINT constructor.
    point_wkt = f"POINT({store.longitude} {store.latitude})"

    db_store = models.Store(
        name=store.name,
        address=store.address,
        latitude=store.latitude,
        longitude=store.longitude,
        chain_name=store.chain_name,
        geom=point_wkt # Pass the WKT string directly
    )
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

# Placeholder for other CRUD functions to be added later
# def get_stores(db: Session, skip: int = 0, limit: int = 100):
#     pass

# def update_store(db: Session, store_id: int, store_update: schemas.StoreUpdate):
#     pass

# def delete_store(db: Session, store_id: int):
#     pass

# def create_promotion(db: Session, promotion: schemas.PromotionCreate):
#     pass

# def get_promotions_for_store(db: Session, store_id: int, skip: int = 0, limit: int = 100):
#     pass
