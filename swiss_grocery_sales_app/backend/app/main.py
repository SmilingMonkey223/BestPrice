from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Assuming geocoding.py is in the same directory 'app'
from .geocoding import fetch_coordinates_from_geo_admin

app = FastAPI()

class AddressRequest(BaseModel):
    address: str

class GeocodeResponse(BaseModel):
    latitude: float
    longitude: float

@app.post("/api/v1/geocode", response_model=GeocodeResponse)
async def geocode_address(request: AddressRequest):
    """
    Geocodes a Swiss address using the GeoAdmin API and returns its latitude and longitude.
    """
    coordinates = await fetch_coordinates_from_geo_admin(request.address)

    if coordinates:
        latitude, longitude = coordinates
        return GeocodeResponse(latitude=latitude, longitude=longitude)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Address not found or could not be geocoded: {request.address}"
        )

# To allow running with uvicorn main:app --reload from the 'backend' directory
# Make sure the import for geocoding is correct if you run this directly.
# For uvicorn, it should be from .geocoding import ...
# If running python app/main.py directly, it might need to be from geocoding import ...
# The provided code uses '.geocoding' which is standard for FastAPI project structures run with uvicorn.
if __name__ == "__main__":
    import uvicorn
    # Note: Running __main__ directly might have issues with relative imports like '.geocoding'
    # It's better to run with 'uvicorn app.main:app --reload' from the 'backend' directory.
    print("Running with uvicorn is recommended: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    # uvicorn.run(app, host="0.0.0.0", port=8000) # Commented out to prevent direct run issues with relative imports
