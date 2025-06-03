from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# --- Promotion Schemas ---

class PromotionBase(BaseModel):
    product_name: str
    sale_price: float # Using float for simplicity, could use Decimal with a custom type
    original_price: Optional[float] = None
    valid_until: Optional[date] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class PromotionCreate(PromotionBase):
    store_id: int # Required when creating a promotion

class PromotionUpdate(PromotionBase):
    # All fields are optional for update
    product_name: Optional[str] = None
    sale_price: Optional[float] = None
    store_id: Optional[int] = None # Allow moving promotion to another store? Or disallow.

class PromotionRead(PromotionBase):
    id: int # PromotionID
    store_id: int
    last_updated: datetime

    class Config:
        orm_mode = True

# --- Store Schemas ---

class StoreBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    chain_name: Optional[str] = None

class StoreCreate(StoreBase):
    pass # No extra fields needed for creation beyond StoreBase

class StoreUpdate(StoreBase):
    # All fields are optional for update
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    chain_name: Optional[str] = None

class StoreRead(StoreBase):
    id: int # StoreID
    # When reading a store, we might want to include its promotions
    promotions: List[PromotionRead] = []

    class Config:
        orm_mode = True

# Schema for the geocode endpoint (already defined in main.py, but good to have all schemas here)
# This is just for reference if we decide to centralize all schemas.
# For now, GeocodeResponse can remain in main.py or be moved here.
# class GeocodeResponse(BaseModel):
#     latitude: float
#     longitude: float

# class AddressRequest(BaseModel):
#     address: str
