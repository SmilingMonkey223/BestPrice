import httpx
from typing import Tuple, Optional

GEOADMIN_API_URL = "https://api3.geo.admin.ch/rest/services/api/SearchServer"

async def fetch_coordinates_from_geo_admin(address: str) -> Optional[Tuple[float, float]]:
    """
    Fetches latitude and longitude for a given Swiss address using the GeoAdmin API.

    Args:
        address: The Swiss address string to geocode.

    Returns:
        A tuple (latitude, longitude) if successful, None otherwise.
    """
    params = {
        "searchText": address,
        "type": "locations",
        "origins": "address",
        "sr": "4326",  # WGS84 for lat/lon
        "limit": "1",
        "geometryFormat": "geojson"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(GEOADMIN_API_URL, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            data = response.json()

            if data.get("features") and len(data["features"]) > 0:
                feature = data["features"][0]
                if feature.get("geometry") and feature["geometry"].get("type") == "Point":
                    coordinates = feature["geometry"].get("coordinates")
                    if coordinates and len(coordinates) == 2:
                        # GeoJSON coordinates are [longitude, latitude]
                        longitude, latitude = coordinates
                        return float(latitude), float(longitude)
            print(f"No features or coordinates found for address: {address}")
            return None
    except httpx.RequestError as e:
        print(f"HTTPX RequestError while fetching coordinates for '{address}': {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"HTTPX HTTPStatusError while fetching coordinates for '{address}': {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching coordinates for '{address}': {e}")
        return None

if __name__ == '__main__':
    # Example usage for testing the function directly
    import asyncio

    async def main():
        test_address = "Bundesplatz 1, 3011 Bern"
        coordinates = await fetch_coordinates_from_geo_admin(test_address)
        if coordinates:
            print(f"Coordinates for '{test_address}': Latitude={coordinates[0]}, Longitude={coordinates[1]}")
        else:
            print(f"Could not fetch coordinates for '{test_address}'.")

        test_address_invalid = "NonExistent Address 123, FantasyLand"
        coordinates_invalid = await fetch_coordinates_from_geo_admin(test_address_invalid)
        if coordinates_invalid:
            print(f"Coordinates for '{test_address_invalid}': Latitude={coordinates_invalid[0]}, Longitude={coordinates_invalid[1]}")
        else:
            print(f"Could not fetch coordinates for '{test_address_invalid}'.")

    asyncio.run(main())
