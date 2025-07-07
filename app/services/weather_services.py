# app/services/weather_services.py
"""Service to fetch weather information from WeatherAPI."""

import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.security.api_key import APIKeyHeader


load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.weatherapi.com/v1/current.json"

api_key_header = APIKeyHeader(name="x-api-key", auto_error=True)


# Dependency: reusable async HTTP client
async def get_http_client() -> httpx.AsyncClient:
    """
    Create and yield an async HTTP client for making requests.

    **Returns:**
    - An instance of `httpx.AsyncClient` with a timeout of 10 seconds.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        yield client


async def get_temperature(client: httpx.AsyncClient, city: str):
    """
    Fetch the current temperature for a given city.

    **Parameters:**
    - `city`: The name of the city to get the temperature for.

    **Returns:**
    - A dictionary containing the city name, country, temperature in Celsius,
      weather condition, and local time in ISO format.

    **Raises:**
    - `httpx.HTTPStatusError`: If the API request fails or the city is not found.
    - `httpx.RequestError`: If there is a network error while making the request.

    **Example output**
    ```
    {
        "city": "London",
        "country": "United Kingdom",
        "temperature_celsius": 15.0,
        "condition": "Partly cloudy",
        "local_time": "2025-07-06T13:28"
    }
    """
    params = {
        "key": API_KEY,
        "q": city,
        "aqi": "no"
    }
    try:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temperature_celsius": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "local_time": data["location"]["localtime"].replace(" ", "T"),
        }
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Weather API error") from exc

    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Network error: {exc}") from exc
