from sqlalchemy.orm import Session
from sqlalchemy import func # For SQL functions like ST_MakePoint, ST_DWithin
from geoalchemy2.types import Geography # For casting geometry to geography
from geoalchemy2.elements import WKTElement # To create geometry elements from WKT
from typing import Optional, List # Ensure List is imported

from . import models
from . import schemas

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
    """
    Retrieves stores within a given radius (in kilometers) from a central point.
    Uses PostGIS ST_DWithin with geography type for accurate distance calculation in meters.
    """
    radius_meters = radius_km * 1000.0

    # Create a geography point from the input lat/lon
    # ST_MakePoint expects (longitude, latitude)
    center_point_geography = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326).cast(Geography)

    # Query stores where the store's geom (cast to geography) is within radius_meters of the center point
    query = db.query(models.Store).filter(
        func.ST_DWithin(
            models.Store.geom.cast(Geography), # Cast store's geometry to geography
            center_point_geography,
            radius_meters
        )
    )

    stores = query.offset(skip).limit(limit).all()
    return stores

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
