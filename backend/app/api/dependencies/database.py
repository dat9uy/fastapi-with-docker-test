from typing import Type, Callable

from databases import Database
from fastapi import Depends

from fastapi.requests import Request
from app.db.repositories.base import BaseRepository


def get_database(request: Request) -> Database:
    return request.app.state.db


def get_repository(repo_type: Type[BaseRepository]) -> Callable:
    def _get_repo(db: Database = Depends(get_database)) -> Type[BaseRepository]:
        return repo_type(db)

    return _get_repo
