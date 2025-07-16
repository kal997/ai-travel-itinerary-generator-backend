import pytest
from jose import jwt

from travelitinerarybackend import security
from travelitinerarybackend.config import config


def test_access_token_expire_minutes():
    assert security.access_token_expire_minute() == 30


def test_create_access_token():
    token = security.create_access_token("email")
    assert {"sub": "email"}.items() <= jwt.decode(
        token, algorithms=[config.ALGORITHM], key=config.SECRET_KEY
    ).items()


# no need for anyio
def test_password_hashes():
    password = "123456"
    hashed_password = security.get_password_hash(password)
    assert security.verify_password(password, hashed_password)


# here anyio is the eventloop that the test will run on
# also we passing the fixture to the test to ensure that there's a created user
@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    print("test_get_user == ", registered_user["email"])
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("dummy.dummy@not_found_dummy.com")
    assert user is None


@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    user = await security.authenticate_user(
        registered_user["email"], registered_user["password"]
    )
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_does_not_exist():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("notfoundemail", "password")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "wrongpassword")


@pytest.mark.anyio
async def test_get_current_user(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token=token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user(token="invalid token")
