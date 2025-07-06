" FastAPI application for a weather service API "
from fastapi import APIRouter, HTTPException
from typing import Any
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from app.api.v1.schemas import WeatherResponse
from app.services.weather_services import get_temperature


router = APIRouter()

@router.get(
    "/weather/{city}",
    response_model=WeatherResponse,
    status_code=HTTP_200_OK,
    summary="Get current temperature by city",
    response_description="Weather data including temperature"
)
async def weather(city: str):
    """
    Get the current temperature for a given city.

    ** Parameters: **
    - `city`: The name of the city to get the temperature for.

    ** Returns: **
    - A dictionary containing the city name and its current temperature in Celsius.
    """
    try:
        weather_data = await get_temperature(city)
        return weather_data
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"City not found or API error: {str(e)}"
        ) from e
