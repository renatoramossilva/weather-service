# app/services/weather_services.py
"""Service to fetch weather information from WeatherAPI."""

import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from typing import AsyncGenerator
from app.services.redis import get_info_from_redis, save_info_redis
import bindl.logger


LOG = bindl.logger.setup_logger(__name__)

# Load .env file
load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.weatherapi.com/v1/current.json"


class GetWeatherInfoError(Exception):
    pass


# Dependency: reusable async HTTP client
async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, httpx.AsyncClient]:
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
    LOG.info("Getting weather info for the search: %r", city)
    cache_key = f"weather_info:v1:{city}"
    cached_city = await get_info_from_redis(cache_key=cache_key)
    if cached_city:
        LOG.info("Returning city info (%r) found in Redis cache", cache_key)
        return cached_city

    params = {"key": API_KEY, "q": city, "aqi": "no"}
    try:
        LOG.info("Get weather info from %r", BASE_URL)
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        LOG.info("Response received with no erros.")

        data = response.json()
        if data:
            result = {
                "city": data["location"]["name"],
                "country": data["location"]["country"],
                "temperature_celsius": data["current"]["temp_c"],
                "condition": data["current"]["condition"]["text"],
                "local_time": data["location"]["localtime"].replace(" ", "T"),
            }
            await save_info_redis(cache_key=cache_key, result=result)
            return result

        else:
            raise GetWeatherInfoError("Error getting info weather from ", BASE_URL)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail="Weather API error"
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Network error: {exc}") from exc
