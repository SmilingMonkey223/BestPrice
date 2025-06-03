from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.types import Geography
from geoalchemy2.elements import WKTElement # Keep if other functions use it
from typing import Optional, List

from . import models
from . import schemas

# --- Store CRUD Functions (existing) ---
def get_store(db: Session, store_id: int) -> Optional[models.Store]:
    return db.query(models.Store).filter(models.Store.id == store_id).first()

def create_store(db: Session, store: schemas.StoreCreate) -> models.Store:
    point_wkt = f"POINT({store.longitude} {store.latitude})"
    db_store = models.Store(
        name=store.name,
        address=store.address,
        latitude=store.latitude,
        longitude=store.longitude,
        chain_name=store.chain_name,
        geom=point_wkt
    )
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

def get_stores_within_radius(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float,
    skip: int = 0,
    limit: int = 100
) -> List[models.Store]:
    radius_meters = radius_km * 1000.0
    center_point_geography = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326).cast(Geography)
    query = db.query(models.Store).filter(
        func.ST_DWithin(
            models.Store.geom.cast(Geography),
            center_point_geography,
            radius_meters
        )
    )
    stores = query.offset(skip).limit(limit).all()
    return stores

# --- Promotion CRUD Functions (new) ---

def create_store_promotion(db: Session, promotion: schemas.PromotionCreate) -> models.Promotion:
    """
    Creates a new promotion associated with a store.
    Assumes promotion.store_id is correctly set in the input schema.
    """
    db_promotion = models.Promotion(
        store_id=promotion.store_id, # Taken from the schema
        product_name=promotion.product_name,
        sale_price=promotion.sale_price,
        original_price=promotion.original_price,
        valid_until=promotion.valid_until,
        description=promotion.description,
        image_url=promotion.image_url
        # last_updated is handled by the database (server_default/onupdate)
    )
    db.add(db_promotion)
    db.commit()
    db.refresh(db_promotion)
    return db_promotion

def get_promotions_for_store(
    db: Session,
    store_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Promotion]:
    """
    Retrieves a list of promotions for a specific store, with pagination.
    """
    return db.query(models.Promotion).filter(models.Promotion.store_id == store_id).offset(skip).limit(limit).all()


# Placeholder for other CRUD functions to be added later
# def get_stores(db: Session, skip: int = 0, limit: int = 100):
#     pass

# def update_store(db: Session, store_id: int, store_update: schemas.StoreUpdate):
#     pass

# def delete_store(db: Session, store_id: int):
#     pass

# def get_promotions_for_store(db: Session, store_id: int, skip: int = 0, limit: int = 100):
#     pass
