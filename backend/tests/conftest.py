import os
import uuid

import docker as pydocker
import pytest
from asgi_lifespan import LifespanManager
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

from app.db.migrate import Migrate
from tests.helpers import pull_image, ping_postgres


@pytest.fixture(scope="session")
def docker() -> pydocker.APIClient:
    with pydocker.APIClient(version="auto") as client:
        yield client


@pytest.fixture(scope="session")
def postgres_container(docker: pydocker.APIClient):
    image = "postgres:12.6-alpine"
    pull_image(docker, image)

    container = docker.create_container(
        image=image,
        name=f"test-postgres-{uuid.uuid4()}",
        detach=True,
        environment=[
            "POSTGRES_USER=datguy",
            "POSTGRES_PASSWORD=ngandethuong",
            "POSTGRES_DB=phresh_test"
        ]
    )

    docker.start(container=container["Id"])
    inspection = docker.inspect_container(container["Id"])
    host = inspection["NetworkSettings"]["IPAddress"]

    dsn = f"postgres://datguy:ngandethuong@{host}/postgres"

    try:
        ping_postgres(dsn)
        os.environ["POSTGRES_DOCKER_SERVER"] = host
        os.environ["DATABASE_URL"] = dsn

        yield container

    finally:
        docker.kill(container["Id"])
        docker.remove_container(container["Id"])


@pytest.fixture(autouse=True)
async def apply_migrations(postgres_container: None) -> None:
    db_migrate = Migrate(db_uri=os.environ["DATABASE_URL"])

    db_migrate.apply()
    yield
    db_migrate.rollback_all()


@pytest.fixture
def app(apply_migrations) -> FastAPI:
    from app.main import get_application

    return get_application()


@pytest.fixture
def db(app: FastAPI) -> Database:
    return app.state.db


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
                app=app, base_url="http://testserver", headers={"Content-Type": "application/json"},
        ) as client:
            yield client
