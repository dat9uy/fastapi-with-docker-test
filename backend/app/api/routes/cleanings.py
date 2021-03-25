from typing import List

from fastapi import APIRouter, status, Body, Depends

from app.api.dependencies.database import get_repository
from app.db.repositories.cleanings import CleaningsRepository
from app.models.cleaning import CleaningPublic, CleaningCreate

router = APIRouter()


@router.get("/")
async def get_all_cleanings() -> List[dict]:
    cleanings = [
        {"id": 1, "name": "My house", "cleaning_type": "full_clean", "price_per_hour": 29.99},
        {"id": 2, "name": "Someone else's house", "cleaning_type": "spot_clean", "price_per_hour": 19.99}
    ]
    return cleanings


@router.post("/", response_model=CleaningPublic, name="cleanings:create-cleaning", status_code=status.HTTP_201_CREATED)
async def create_new_cleaning(
        new_cleaning: CleaningCreate = Body(..., embed=True),
        cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> CleaningPublic:
    return await cleanings_repo.create_cleaning(new_cleaning=new_cleaning)