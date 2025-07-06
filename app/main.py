" FastAPI application for a weather service API "
from fastapi import FastAPI
from app.api.v1.routes import router as api_router

app = FastAPI(title="Weather Service API")

app.include_router(api_router, prefix="/api/v1")
