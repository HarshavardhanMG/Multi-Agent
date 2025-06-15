# In utils/api_helpers.py

import aiohttp
import json
from typing import Dict, Any, Optional
from .config import settings

# REWRITTEN: This function now fetches all locations and finds the one with the matching ID.
async def get_location_details(location_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information for a specific location by fetching all locations
    and finding the one with the matching ID.
    """
    if not location_id:
        return None
    
    # This is a known working endpoint that returns a list of all locations.
    url = "https://fdo.rocketlaunch.live/json/locations"
    
    async with aiohttp.ClientSession() as session:
        # We explicitly ask for 'application/json' to be safe.
        headers = {'Accept': 'application/json'}
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"Failed to fetch locations list. Status: {response.status}")
                return None
            
            try:
                # Tell the JSON decoder to ignore the incorrect content-type if necessary.
                data = await response.json(content_type=None)
            except json.JSONDecodeError:
                print("Failed to decode JSON from locations endpoint.")
                return None

            if data and data.get("result"):
                # Find the specific location by its ID in the list of results.
                for location in data["result"]:
                    if location.get("id") == location_id:
                        return location
                print(f"Warning: Location with ID {location_id} not found in the list.")
            
            return None


# get_spacex_launch remains the same
async def get_spacex_launch() -> Dict[str, Any]:
    """
    Get the next SpaceX launch by fetching a list of upcoming launches
    from the Rocket Launch Live API and finding the first one from SpaceX.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.ROCKETLAUNCH_LIVE_API_ENDPOINT) as response:
            if response.status != 200:
                raise Exception(f"RocketLaunch.Live API error: {response.status} {await response.text()}")
            
            data = await response.json()
            launches = data.get("result", [])

            if not launches:
                raise Exception("No upcoming launches found from RocketLaunch.Live API.")

            for launch in launches:
                provider_name = launch.get("provider", {}).get("name")
                if provider_name and "spacex" in provider_name.lower():
                    return launch
            
            raise Exception("No SpaceX launch found in the next 5 upcoming launches.")

# get_weather remains the same
async def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Get weather information for a specific location."""
    async with aiohttp.ClientSession() as session:
        params = {"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_API_KEY, "units": "metric"}
        async with session.get(settings.OPENWEATHER_API_ENDPOINT, params=params) as response:
            if response.status == 200:
                return await response.json()
            raise Exception(f"OpenWeather API error: {response.status}")

# get_coordinates_from_location is not used in the primary flow but can be kept.
async def get_coordinates_from_location(location_name: str, state: str, country: str) -> Optional[Dict[str, float]]:
    """
    Get coordinates for a location using OpenWeather's geocoding API.
    """
    async with aiohttp.ClientSession() as session:
        query = f"{location_name},{state},{country}"
        params = {"q": query, "appid": settings.OPENWEATHER_API_KEY, "limit": 1}
        async with session.get("http://api.openweathermap.org/geo/1.0/direct", params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data and len(data) > 0:
                    return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
            return None

# extract_launch_location remains the same as the previous fix.
async def extract_launch_location(launch_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """
    Extracts launch location coordinates by getting the location ID from the
    launch data and making a second API call to get detailed location info.
    """
    try:
        location_id = launch_data.get("pad", {}).get("location", {}).get("id")

        if not location_id:
            print("Warning: Location ID not found in launch data.")
            return None

        print(f"Found location ID: {location_id}. Fetching details...")
        location_details = await get_location_details(location_id)
        
        if not location_details:
            print("Warning: Could not retrieve location details from the API.")
            return None

        latitude = location_details.get("latitude")
        longitude = location_details.get("longitude")

        if latitude is not None and longitude is not None:
            print(f"Successfully extracted coordinates: Lat {latitude}, Lon {longitude}")
            return {"lat": float(latitude), "lon": float(longitude)}
        else:
            print("Warning: Latitude or Longitude not found in location details.")
            return None

    except (ValueError, TypeError, KeyError) as e:
        print(f"Error processing launch data for location: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in extract_launch_location: {e}")
        return None

# analyze_weather_impact remains the same
def analyze_weather_impact(weather_data: Dict[str, Any], launch_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        weather = weather_data.get("weather", [{}])[0]
        main = weather_data.get("main", {})
        wind = weather_data.get("wind", {})
        
        conditions = {
            "description": weather.get("description", "N/A"),
            "temperature": main.get("temp", "N/A"),
            "wind_speed": wind.get("speed", "N/A"),
            "clouds": weather_data.get("clouds", {}).get("all", "N/A")
        }
        
        impacts = []
        if isinstance(conditions["wind_speed"], (int, float)) and conditions["wind_speed"] > 15:
            impacts.append("High winds may exceed launch constraints.")
        if isinstance(conditions["clouds"], (int, float)) and conditions["clouds"] > 80:
            impacts.append("Heavy cloud cover may affect optical tracking.")
        if any(x in conditions["description"].lower() for x in ["rain", "thunderstorm", "storm", "squalls"]):
            impacts.append("Precipitation or storm activity is a significant concern.")
        
        return {
            "conditions": conditions,
            "potential_impacts": impacts if impacts else ["Weather conditions appear favorable."],
        }
    except Exception as e:
        raise Exception(f"Error analyzing weather impact: {str(e)}")