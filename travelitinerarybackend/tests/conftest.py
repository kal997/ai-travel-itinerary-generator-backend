# will contains the test fixtures


import os
from typing import AsyncGenerator, Generator

import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# whenever this module is imported (pytest) change the ENV_STATE to test
os.environ["ENV_STATE"] = "test"

from travelitinerarybackend.config import config
from travelitinerarybackend.database import database, metadata, user_table

# the overwrite has to be before importing app->importing config-> gets test
from travelitinerarybackend.main import app

# Ensure SQLite file-based DB is created with schema
if config.DATABASE_URL.startswith("sqlite"):
    engine = sqlalchemy.create_engine("sqlite:///test.db")
    metadata.create_all(engine)


# fixture to run every pytest session, to define the async platform to be used with async tests (use asyncio)
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# the client we will interact with instead of starting the fastapi server
# it is a fixture because it will be injected in all of the tests
@pytest.fixture()
def client() -> Generator:
    # before starting the client
    yield TestClient(app)
    # teardown after exiting


# we also need to clear the tables before running any test
# it is a fixture because it will be injected in all of the tests, auto use to clean the db
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await (
        database.disconnect()
    )  # will delete everything inside the db because rollback is true


# we will use this fixture in all handlers tests
# use client as dependency injection
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac


# fiture to be used with test that we want a created user to be exist in the db
@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "dummy.dummy@dummy.com", "password": "123456"}
    await async_client.post("/register", json=user_details)

    # to get the id
    query = user_table.select().where(user_table.c.email == user_details["email"])
    # we are sure it's there
    user = await database.fetch_one(query)
    if user:
        user_details["id"] = user.id

    print(user_details)
    return user_details


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, registered_user: dict) -> str:
    response = await async_client.post(
        "/token",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
            "grant_type": "password",
        },
    )

    return response.json()["access_token"]
