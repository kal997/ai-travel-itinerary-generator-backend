import pytest
from httpx import AsyncClient

from travelitinerarybackend.models.itinerary import UserItineraryIn


# helper function to create an itinerary
async def create_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: list[str],
    async_client: AsyncClient,
) -> dict:
    # the async_client we have configured in conftest
    response = await async_client.post(
        "/itinerary",
        json={
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "interests": interests,
        },
    )

    return response.json()


# fixture to be used in all itinerary tests, this fixture makes sure that there's a post that's already
# exists at the time of the test is executed
@pytest.fixture()
async def created_itinerary(async_client: AsyncClient) -> dict:
    return await create_itinerary(
        destination="Paris",
        start_date="2025-08-01",
        end_date="2025-08-10",
        interests=["food", "entertainment"],
        async_client=async_client,
    )


# test itinerary creation
@pytest.mark.anyio
async def test_create_itinerary(async_client: AsyncClient):
    user_itinerary = UserItineraryIn(
        destination="Cairo",
        start_date="2025-08-01",
        end_date="2025-08-10",
        interests=["food", "history"],
    )

    response = await async_client.post(
        "/api/itinerary", json=user_itinerary.model_dump()
    )

    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Cairo"
    assert data["start_date"] == "2025-08-01"
    assert data["end_date"] == "2025-08-10"
    assert data["interests"] == ["food", "history"]
