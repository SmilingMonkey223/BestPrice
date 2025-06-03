from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AddressRequest(BaseModel):
    address: str

class GeocodeResponse(BaseModel):
    latitude: float
    longitude: float

@app.post("/api/v1/geocode", response_model=GeocodeResponse)
async def geocode_address(request: AddressRequest):
    # Mock response for now
    # Later, this will call the GeoAdmin API
    print(f"Received address: {request.address}") # For logging/debugging
    return GeocodeResponse(latitude=47.3769, longitude=8.5417)

# To allow running with uvicorn main:app --reload from the 'backend' directory
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
