from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import ping, test, dataset

api_router = APIRouter()

api_router.include_router(ping.router, prefix="/ping", tags=["ping"])
api_router.include_router(test.router, prefix="/test", tags=["test"])

api_router.include_router(dataset.router, prefix="/dataset", tags=["dataset"])