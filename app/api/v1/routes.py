" FastAPI application for a weather service API "
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def hello() -> dict:
    """
    A simple endpoint that returns a greeting message.
    """
    return {"message": "Hello, World!"}
