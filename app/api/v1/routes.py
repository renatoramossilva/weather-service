"FastAPI application for a weather service API"

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
import httpx
from bindl.prometheus_wrapper.metrics_exporter import MetricsExporter
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from app.api.v1.schemas import WeatherResponse
from app.services.weather_services import get_temperature, get_http_client


router = APIRouter()

HttpClientDependency = Annotated[httpx.AsyncClient, Depends(get_http_client)]

exporter = MetricsExporter(port=8082)
exporter.register_counter("requests_total", "Total number of requests", label_names=["method", "endpoint"])
exporter.register_counter("failed_requests_total", "Total number of failed requests", label_names=["method", "endpoint"])


@router.get(
    "/weather/{city}",
    response_model=WeatherResponse,
    status_code=HTTP_200_OK,
    summary="Get current temperature by city",
    response_description="Weather data including temperature",
)
async def weather(
    city: str,
    client: HttpClientDependency,
) -> WeatherResponse:
    """
    Get the current temperature for a given city.

    **Parameters:**
    - `client`: An async HTTP client for making requests.
    - `city`: The name of the city to get the temperature for.

    **Returns:**
    - A dictionary containing the city name and its current temperature in Celsius.
    """
    try:
        return await get_temperature(client, city)
    except Exception as e:
        exporter.inc_counter("failed_requests_total", labels={"method": "GET", "endpoint": "/app/api/v1/routes/weather"})
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"City not found or API error: {str(e)}",
        ) from e
    finally:
        exporter.inc_counter("requests_total", labels={"method": "GET", "endpoint": "/app/api/v1/routes/weather"})
