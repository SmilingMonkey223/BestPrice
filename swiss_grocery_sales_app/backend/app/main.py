from fastapi import FastAPI, HTTPException, Depends, Query # Added Query
from sqlalchemy.orm import Session
from typing import List # Added List

# Relative imports for modules within the 'app' package
from . import crud, models, schemas
from .database import get_db
from .geocoding import fetch_coordinates_from_geo_admin

app = FastAPI(
    title="Swiss Grocery Sales Aggregator API",
    description="API for finding grocery sales and promotions in Switzerland.",
    version="0.1.0"
)

# --- Geocoding Endpoint (existing) ---
@app.post("/api/v1/geocode", response_model=schemas.GeocodeResponse, tags=["Geocoding"])
async def geocode_address(request: schemas.AddressRequest):
    coordinates = await fetch_coordinates_from_geo_admin(request.address)
    if coordinates:
        latitude, longitude = coordinates
        return schemas.GeocodeResponse(latitude=latitude, longitude=longitude)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Address not found or could not be geocoded: {request.address}"
        )

# --- Store Endpoints ---

@app.post("/api/v1/stores", response_model=schemas.StoreRead, status_code=201, tags=["Stores"])
def create_new_store(store: schemas.StoreCreate, db: Session = Depends(get_db)):
    created_store = crud.create_store(db=db, store=store)
    return created_store

@app.get("/api/v1/stores/{store_id}", response_model=schemas.StoreRead, tags=["Stores"])
def read_store(store_id: int, db: Session = Depends(get_db)):
    db_store = crud.get_store(db=db, store_id=store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")
    return db_store

@app.get("/api/v1/stores", response_model=List[schemas.StoreRead], tags=["Stores"])
def read_stores_nearby(
    latitude: float = Query(..., description="Latitude of the center point for the search."),
    longitude: float = Query(..., description="Longitude of the center point for the search."),
    radius_km: float = Query(10.0, gt=0, le=50, description="Search radius in kilometers (max 50km)."),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return (max 200)."),
    db: Session = Depends(get_db)
):
    """
    Retrieves grocery stores within a specified radius from a central point (latitude, longitude).
    Results are paginated.
    """
    stores = crud.get_stores_within_radius(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        skip=skip,
        limit=limit
    )
    return stores

# Main block (existing)
if __name__ == "__main__":
    print("Running with uvicorn is recommended: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
