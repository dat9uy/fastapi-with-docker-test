from app.db.repositories.base import BaseRepository
from app.models.cleaning import CleaningCreate, CleaningInDB

CREATE_CLEANING_QUERY = """
    INSERT INTO cleanings (name, description, price, cleaning_type)
    VALUES (:name, :description, :price, :cleaning_type)
    RETURNING id, name, description, price, cleaning_type
"""


class CleaningsRepository(BaseRepository):
    async def create_cleaning(self, *, new_cleaning: CleaningCreate) -> CleaningInDB:
        cleaning = await self.db.fetch_one(query=CREATE_CLEANING_QUERY, values=new_cleaning.dict())
        return CleaningInDB.parse_obj(cleaning)
