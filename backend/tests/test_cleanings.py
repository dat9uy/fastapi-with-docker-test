from typing import List, Union

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from pydantic import parse_obj_as

from app.models.cleaning import CleaningCreate, CleaningInDB

pytestmark = pytest.mark.asyncio


@pytest.fixture
def new_cleaning():
    return CleaningCreate(
        name="test cleaning",
        description="test description",
        price=0.00,
        cleaning_type='spot_clean'
    )


class TestCleaningsRoutes:

    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"), json={})
        assert res.status_code != status.HTTP_404_NOT_FOUND

    async def test_invalid_input_raises_error(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"), json={})
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateCleaning:
    async def test_valid_input_creates_cleaning(self,
                                                app: FastAPI,
                                                client: AsyncClient,
                                                new_cleaning: CleaningCreate) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"),
                                json={"new_cleaning": new_cleaning.dict()})

        assert res.status_code == status.HTTP_201_CREATED

        created_cleaning = CleaningCreate.parse_obj(res.json())
        assert created_cleaning == new_cleaning

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
                (None, 422),
                ({}, 422),
                ({"name": "test_name"}, 422),
                ({"price": 10.00}, 422),
                ({"name": "test_name", "description": "test"}, 422),
        ),
    )
    async def test_invalid_input_raises_error(
            self, app: FastAPI, client: AsyncClient, invalid_payload: dict, status_code: int
    ) -> None:
        res = await client.post(
            app.url_path_for("cleanings:create-cleaning"), json={"new_cleaning": invalid_payload}
        )
        assert res.status_code == status_code


class TestGetCleaning:
    async def test_get_cleaning_by_id(self, app: FastAPI, client: AsyncClient, sample_cleaning: CleaningInDB) -> None:
        res = await client.get(app.url_path_for("cleanings:get-cleaning-by-id", cleaning_id=sample_cleaning.id))
        assert res.status_code == status.HTTP_200_OK

        cleaning = CleaningInDB.parse_obj(res.json())
        assert cleaning.id == 1

    @pytest.mark.parametrize(
        "wrong_id, status_code",
        (
                (0, 404),
                (-1, 404),
                (None, 422),
        ),
    )
    async def test_wrong_id_returns_error(
            self, app: FastAPI, client: AsyncClient, wrong_id: int, status_code: int
    ) -> None:
        res = await client.get(app.url_path_for("cleanings:get-cleaning-by-id", cleaning_id=wrong_id))
        assert res.status_code == status_code

    async def test_get_all_cleanings_return_valid_response(
            self, app: FastAPI, client: AsyncClient, sample_cleaning: CleaningInDB) -> None:
        res = await client.get(app.url_path_for("cleanings:get-all-cleanings"))
        assert res.status_code == status.HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0

        all_cleanings = parse_obj_as(List[CleaningInDB], res.json())
        assert sample_cleaning in all_cleanings


class TestUpdateCleaning:
    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
                (["name"], ["new fake cleaning name"]),
                (["description"], ["new fake cleaning description"]),
                (["price"], [3.14]),
                (["cleaning_type"], ["full_clean"]),
                (["name", "description"], ["extra new fake cleaning name", "extra new fake cleaning description"]),
                (["price", "cleaning_type"], [42.00, "dust_up"]),
        ),
    )
    async def test_update_cleaning_with_valid_input(
            self, app: FastAPI, client: AsyncClient, sample_cleaning: CleaningInDB,
            attrs_to_change: List[str], values: List[Union[str, int]]
    ) -> None:
        cleaning_update = {"cleaning_update": {attrs_to_change[i]: values[i] for i, _ in enumerate(attrs_to_change)}}

        res = await client.put(
            app.url_path_for("cleanings:update-cleaning-by-id", cleaning_id=sample_cleaning.id),
            json=cleaning_update
        )
        assert res.status_code == status.HTTP_200_OK

        updated_cleaning = CleaningInDB.parse_obj(res.json())
        assert updated_cleaning.id == sample_cleaning.id

        # make sure that any attribute we updated has changed to the correct value
        for i in range(len(attrs_to_change)):
            assert getattr(updated_cleaning, attrs_to_change[i]) != getattr(sample_cleaning, attrs_to_change[i])
            assert getattr(updated_cleaning, attrs_to_change[i]) == values[i]

    @pytest.mark.parametrize(
        "cleaning_id, payload, status_code",
        (
                (-1, {"name": "test"}, 422),
                (0, {"name": "test2"}, 422),
                (500, {"name": "test3"}, 404),
                (1, None, 422),
                (1, {"cleaning_type": "invalid cleaning type"}, 422),
                (1, {"name": "test 4", "cleaning_type": None}, 400),
        ),
    )
    async def test_update_cleaning_with_invalid_input_throws_error(
            self,
            app: FastAPI,
            client: AsyncClient,
            sample_cleaning: CleaningInDB,
            cleaning_id: int,
            payload: dict,
            status_code: int,
    ) -> None:
        cleaning_update = {"cleaning_update": payload}

        res = await client.put(
            app.url_path_for("cleanings:update-cleaning-by-id", cleaning_id=cleaning_id),
            json=cleaning_update
        )
        assert res.status_code == status_code


class TestDeleteCleaning:
    async def test_can_delete_cleaning_successfully(
            self, app: FastAPI, client: AsyncClient, sample_cleaning: CleaningInDB
    ) -> None:
        # delete the cleaning
        res = await client.delete(app.url_path_for("cleanings:delete-cleaning-by-id", cleaning_id=sample_cleaning.id))
        assert res.status_code == status.HTTP_200_OK

        # ensure that cleaning doesn't exist
        res = await client.get(app.url_path_for("cleanings:get-cleaning-by-id", cleaning_id=sample_cleaning.id))
        assert res.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "cleaning_id, status_code",
        (
                (500, 404),
                (0, 422),
                (-1, 422),
                (None, 422),
        ),
    )
    async def test_can_delete_cleaning_successfully(
            self, app: FastAPI, client: AsyncClient, sample_cleaning: CleaningInDB, cleaning_id: int, status_code: int
    ) -> None:
        res = await client.delete(app.url_path_for("cleanings:delete-cleaning-by-id", cleaning_id=cleaning_id))
        assert res.status_code == status_code
