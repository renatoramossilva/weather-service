"FastAPI application for a weather service API"

from fastapi import FastAPI
from app.api.v1.routes import router as api_router

app = FastAPI(
    title="🌤️ Weather API",
    description="Get real-time weather data by city.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Weather API is running"}


app.include_router(api_router, prefix="/api/v1")
