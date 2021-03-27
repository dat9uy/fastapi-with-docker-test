from typing import List

from fastapi import HTTPException, status
from pydantic import parse_obj_as
from loguru import logger

from app.db.repositories.base import BaseRepository
from app.models.cleaning import CleaningCreate, CleaningInDB, CleaningUpdate

CREATE_CLEANING_QUERY = """
    INSERT INTO cleanings (name, description, price, cleaning_type)
    VALUES (:name, :description, :price, :cleaning_type)
    RETURNING id, name, description, price, cleaning_type
"""

GET_CLEANING_BY_ID_QUERY = """
    SELECT id, name, description, price, cleaning_type
    FROM cleanings
    WHERE id = :id
"""

GET_ALL_CLEANINGS_QUERY = """
    SELECT id, name, description, cleaning_type, price
    FROM cleanings
"""

UPDATE_CLEANING_BY_ID_QUERY = """
    UPDATE cleanings
    
    SET name = :name,
        description = :description,
        price = :price,
        cleaning_type = :cleaning_type
        
    WHERE id = :id
    RETURNING id, name, description, price, cleaning_type
"""

DELETE_CLEANING_BY_ID_QUERY = """
    DELETE FROM cleanings
    WHERE id = :id
    RETURNING id
"""


class CleaningsRepository(BaseRepository):
    async def create_cleaning(self, *, new_cleaning: CleaningCreate) -> CleaningInDB:
        cleaning = await self.db.fetch_one(query=CREATE_CLEANING_QUERY, values=new_cleaning.dict())
        return CleaningInDB.parse_obj(cleaning)

    async def get_cleaning_by_id(self, *, get_id: int):
        cleaning = await self.db.fetch_one(query=GET_CLEANING_BY_ID_QUERY, values={"id": get_id})

        if not cleaning:
            return None

        return CleaningInDB.parse_obj(cleaning)

    async def get_all_cleanings(self):
        cleaning_records = await self.db.fetch_all(query=GET_ALL_CLEANINGS_QUERY)
        return parse_obj_as(List[CleaningInDB], cleaning_records)

    async def update_cleaning(self, *, update_id: int, cleaning_update: CleaningUpdate) -> CleaningInDB:
        cleaning = await self.get_cleaning_by_id(get_id=update_id)

        if not cleaning:
            return None

        cleaning_update_params = cleaning.copy(update=cleaning_update.dict(exclude_unset=True))
        if cleaning_update_params.cleaning_type is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid cleaning type. Cannot be None.")

        try:
            updated_cleaning = await self.db.fetch_one(
                query=UPDATE_CLEANING_BY_ID_QUERY, values=cleaning_update_params.dict()
            )

            return CleaningInDB.parse_obj(updated_cleaning)

        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid update params.")

    async def delete_cleanings_by_id(self, delete_id: int):
        cleaning = await self.get_cleaning_by_id(get_id=delete_id)

        if not cleaning:
            return None

        return await self.db.execute(query=DELETE_CLEANING_BY_ID_QUERY, values={"id": delete_id})
