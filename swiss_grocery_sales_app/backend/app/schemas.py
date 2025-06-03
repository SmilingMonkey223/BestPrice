from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime

# --- Geocoding Schemas ---
class AddressRequest(BaseModel):
    address: str

class GeocodeResponse(BaseModel):
    latitude: float
    longitude: float

# --- Promotion Schemas ---
class PromotionBase(BaseModel):
    product_name: str
    sale_price: float
    original_price: Optional[float] = None
    valid_until: Optional[date] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class PromotionCreate(PromotionBase):
    store_id: int

class PromotionUpdate(PromotionBase):
    product_name: Optional[str] = None
    sale_price: Optional[float] = None
    store_id: Optional[int] = None

class PromotionRead(PromotionBase):
    id: int
    store_id: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Store Schemas ---
class StoreBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    chain_name: Optional[str] = None

class StoreCreate(StoreBase):
    pass

class StoreUpdate(StoreBase):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    chain_name: Optional[str] = None

class StoreRead(StoreBase):
    id: int
    promotions: List[PromotionRead] = []

    model_config = ConfigDict(from_attributes=True)
