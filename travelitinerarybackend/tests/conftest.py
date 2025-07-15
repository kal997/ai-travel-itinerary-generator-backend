# will contains the test fixtures


import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# whenever this module is imported (pytest) change the ENV_STATE to test
os.environ["ENV_STATE"] = "test"
from travelitinerarybackend.database import database

# the overwrite has to be before importing app->importing config-> gets test
from travelitinerarybackend.main import app


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
