from fastapi import APIRouter
from app.api.routes.cleanings import router as cleaning_router

router = APIRouter()

router.include_router(cleaning_router, prefix="/cleanings", tags=["cleanings"])
