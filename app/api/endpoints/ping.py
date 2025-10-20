from fastapi import APIRouter

router = APIRouter()


# Check if the service is up
@router.get("/service")
async def service_status():
    return 200
