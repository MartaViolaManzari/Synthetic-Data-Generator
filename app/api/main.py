from fastapi import APIRouter
from app.api.endpoints import ping, test

api_router = APIRouter()
api_router.include_router(ping.router, prefix="/ping", tags=["ping"])
api_router.include_router(test.router, prefix="/test", tags=["test"])
