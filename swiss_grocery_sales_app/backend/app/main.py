from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

# Relative imports for modules within the 'app' package
from . import crud, models, schemas # Ensure models is imported if Base.metadata.create_all is called here
from .database import SessionLocal, engine, get_db # Assuming get_db is defined in database.py
from .geocoding import fetch_coordinates_from_geo_admin

# If you plan to use Alembic for migrations, you might not call create_all here.
# For now, if you want to ensure tables are created when the app starts (for dev):
# models.Base.metadata.create_all(bind=engine)
# However, it's better to manage table creation explicitly (e.g. via models.py script or Alembic)

app = FastAPI(
    title="Swiss Grocery Sales Aggregator API",
    description="API for finding grocery sales and promotions in Switzerland.",
    version="0.1.0"
)

# Schemas for Geocoding are now in schemas.py

@app.post("/api/v1/geocode", response_model=schemas.GeocodeResponse, tags=["Geocoding"])
async def geocode_address(request: schemas.AddressRequest):
    """
    Geocodes a Swiss address using the GeoAdmin API and returns its latitude and longitude.
    """
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
    """
    Creates a new grocery store.
    The latitude and longitude provided will be used to generate the store's geometry.
    """
    # Optional: Check if a store with the same name and address already exists if needed
    # db_store_existing = db.query(models.Store).filter(models.Store.name == store.name, models.Store.address == store.address).first()
    # if db_store_existing:
    #     raise HTTPException(status_code=400, detail="Store with this name and address already exists")

    created_store = crud.create_store(db=db, store=store)
    return created_store

@app.get("/api/v1/stores/{store_id}", response_model=schemas.StoreRead, tags=["Stores"])
def read_store(store_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific grocery store by its ID.
    Includes a list of its current promotions.
    """
    db_store = crud.get_store(db=db, store_id=store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")
    return db_store

# To allow running with uvicorn main:app --reload from the 'backend' directory
if __name__ == "__main__":
    print("Running with uvicorn is recommended: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    # Example of how you might explicitly create tables if not using Alembic and not doing it on app load.
    # print("Creating database tables if they don't exist...")
    # models.create_db_tables() # Assuming you have this function in models.py
    # print("Database tables checked/created.")
