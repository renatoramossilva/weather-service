# app/services/weather_services.py
"""Service to fetch weather information from WeatherAPI."""

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.weatherapi.com/v1/current.json"


async def get_temperature(city: str):
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
    async with httpx.AsyncClient() as client:
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