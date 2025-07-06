""" Schemas for the weather service API. """
from pydantic import BaseModel
from pydantic import Field


class WeatherResponse(BaseModel):
    """Schema for the weather response."""
    city: str
    country: str
    temperature_celsius: float
    condition: str
    local_time: str  # ISO format, e.g., "2025-07-06T13:28"
