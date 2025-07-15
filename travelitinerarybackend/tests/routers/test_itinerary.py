import pytest
from httpx import AsyncClient


# Helper function to generate an itinerary (no save)
async def generate_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: list[str],
    async_client: AsyncClient,
) -> dict:
    """Generate itinerary for preview"""
    response = await async_client.post(
        "/api/itinerary/generate",
        json={
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "interests": interests,
        },
    )
    return response.json()


# Helper function to save generated itinerary
async def save_generated_itinerary(
    generated_data: dict,
    async_client: AsyncClient,
) -> dict:
    """Save a generated itinerary to database"""
    response = await async_client.post(
        "/api/itinerary",
        json=generated_data,
    )
    return response.json()


# Fixture that generates AND saves an itinerary
@pytest.fixture()
async def created_itinerary(async_client: AsyncClient) -> dict:
    """Generate and save an itinerary for testing"""
    # Step 1: Generate
    generated = await generate_itinerary(
        destination="Paris",
        start_date="2025-08-01",
        end_date="2025-08-10",
        interests=["food", "entertainment"],
        async_client=async_client,
    )

    # Step 2: Save
    saved = await save_generated_itinerary(generated, async_client)
    return saved


# Test generate endpoint (no save)
@pytest.mark.anyio
async def test_generate_itinerary(async_client: AsyncClient):
    """Test generating itinerary without saving"""
    user_input = {
        "destination": "Cairo",
        "start_date": "2025-08-01",
        "end_date": "2025-08-10",
        "interests": ["food", "history"],
    }

    response = await async_client.post("/api/itinerary/generate", json=user_input)

    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Cairo"
    assert data["start_date"] == "2025-08-01"
    assert data["end_date"] == "2025-08-10"
    assert data["days_count"] == 10
    assert data["interests"] == ["food", "history"]
    assert "itinerary" in data
    assert len(data["itinerary"]) == 10  # 10 days


# Test save endpoint
@pytest.mark.anyio
async def test_save_itinerary(async_client: AsyncClient):
    """Test saving a generated itinerary"""
    # Step 1: Generate
    user_input = {
        "destination": "Cairo",
        "start_date": "2025-08-01",
        "end_date": "2025-08-10",
        "interests": ["food", "history"],
    }

    generate_response = await async_client.post(
        "/api/itinerary/generate", json=user_input
    )
    generated_data = generate_response.json()

    # Step 2: Save
    save_response = await async_client.post("/api/itinerary", json=generated_data)

    assert save_response.status_code == 200
    saved_data = save_response.json()

    # Check it has database fields
    assert "id" in saved_data
    assert "created_at" in saved_data
    assert saved_data["destination"] == "Cairo"
    assert saved_data["days_count"] == 10
    assert "generated_itinerary" in saved_data
    assert len(saved_data["generated_itinerary"]) == 10


# Test generate with invalid data
@pytest.mark.anyio
async def test_generate_itinerary_invalid_dates(async_client: AsyncClient):
    """Test generate with invalid date range"""
    user_input = {
        "destination": "Cairo",
        "start_date": "2025-08-10",  # End before start
        "end_date": "2025-08-01",
        "interests": ["food", "history"],
    }

    response = await async_client.post("/api/itinerary/generate", json=user_input)
    assert response.status_code == 422  # Pydantic validation error


# Test save with missing data
@pytest.mark.anyio
async def test_save_itinerary_missing_body(async_client: AsyncClient):
    """Test save with empty body"""
    response = await async_client.post("/api/itinerary", json={})
    assert response.status_code == 422


# Test save with incomplete data
@pytest.mark.anyio
async def test_save_itinerary_missing_fields(async_client: AsyncClient):
    """Test save with missing required fields"""
    incomplete_data = {
        "destination": "Rome",
        "start_date": "2025-08-01",
        # Missing end_date, days_count, interests, itinerary
    }
    
    response = await async_client.post("/api/itinerary", json=incomplete_data)
    assert response.status_code == 422


# Test get all saved itineraries
@pytest.mark.anyio
async def test_get_all_itineraries(async_client: AsyncClient, created_itinerary: dict):
    """Test retrieving all saved itineraries"""
    response = await async_client.get("/api/itinerary")

    assert response.status_code == 200
    itineraries = response.json()
    assert len(itineraries) == 1
    assert itineraries[0]["id"] == created_itinerary["id"]
    assert itineraries[0]["destination"] == created_itinerary["destination"]


# Test get all when no itineraries exist
@pytest.mark.anyio
async def test_get_all_itineraries_empty(async_client: AsyncClient):
    """Test retrieving itineraries when none exist"""
    response = await async_client.get("/api/itinerary")
    
    assert response.status_code == 200
    assert response.json() == []


# Test delete itinerary
@pytest.mark.anyio
async def test_delete_itinerary(async_client: AsyncClient, created_itinerary: dict):
    """Test deleting a saved itinerary"""
    itinerary_id = created_itinerary["id"]

    # Delete
    delete_response = await async_client.delete(f"/api/itinerary/{itinerary_id}")
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    assert "message" in delete_data
    assert str(itinerary_id) in delete_data["message"]

    # Verify it's gone
    get_response = await async_client.get("/api/itinerary")
    assert len(get_response.json()) == 0


# Test delete non-existent itinerary
@pytest.mark.anyio
async def test_delete_nonexistent_itinerary(async_client: AsyncClient):
    """Test deleting an itinerary that doesn't exist"""
    response = await async_client.delete("/api/itinerary/999")
    assert response.status_code == 404


# Test update itinerary (always regenerates)
@pytest.mark.anyio
async def test_update_itinerary(async_client: AsyncClient, created_itinerary: dict):
    """Test updating a saved itinerary - should regenerate"""
    itinerary_id = created_itinerary["id"]

    # Update with new data (same format as UserItineraryIn)
    new_data = {
        "destination": "Rome",
        "start_date": "2025-09-01",
        "end_date": "2025-09-05",
        "interests": ["history", "art"],
    }

    # Update
    update_response = await async_client.patch(
        f"/api/itinerary/{itinerary_id}", json=new_data
    )
    assert update_response.status_code == 200

    updated_data = update_response.json()
    assert updated_data["destination"] == "Rome"
    assert updated_data["days_count"] == 5
    assert updated_data["interests"] == ["history", "art"]
    assert updated_data["start_date"] == "2025-09-01"
    assert updated_data["end_date"] == "2025-09-05"
    
    # Should have regenerated itinerary
    assert "generated_itinerary" in updated_data
    assert len(updated_data["generated_itinerary"]) == 5  # 5 days
    
    # Verify the ID stayed the same
    assert updated_data["id"] == itinerary_id


# Test update with invalid data
@pytest.mark.anyio
async def test_update_itinerary_invalid_dates(async_client: AsyncClient, created_itinerary: dict):
    """Test updating with invalid date range"""
    itinerary_id = created_itinerary["id"]
    
    invalid_data = {
        "destination": "Rome",
        "start_date": "2025-09-10",  # End before start
        "end_date": "2025-09-05",
        "interests": ["history"],
    }

    response = await async_client.patch(f"/api/itinerary/{itinerary_id}", json=invalid_data)
    assert response.status_code == 422  # Pydantic validation error


# Test update non-existent itinerary
@pytest.mark.anyio
async def test_update_nonexistent_itinerary(async_client: AsyncClient):
    """Test updating an itinerary that doesn't exist"""
    update_data = {
        "destination": "Rome",
        "start_date": "2025-09-01",
        "end_date": "2025-09-05",
        "interests": ["history"],
    }
    
    response = await async_client.patch("/api/itinerary/999", json=update_data)
    assert response.status_code == 404


# Test update with missing fields
@pytest.mark.anyio
async def test_update_itinerary_missing_fields(async_client: AsyncClient, created_itinerary: dict):
    """Test updating with missing required fields"""
    itinerary_id = created_itinerary["id"]
    
    incomplete_data = {
        "destination": "Rome",
        # Missing start_date, end_date, interests
    }

    response = await async_client.patch(f"/api/itinerary/{itinerary_id}", json=incomplete_data)
    assert response.status_code == 422


# Test complete workflow: generate -> save -> update -> delete
@pytest.mark.anyio
async def test_complete_workflow(async_client: AsyncClient):
    """Test the complete itinerary workflow"""
    # Step 1: Generate
    generate_data = {
        "destination": "Tokyo",
        "start_date": "2025-10-01",
        "end_date": "2025-10-07",
        "interests": ["culture", "food"],
    }
    
    generate_response = await async_client.post("/api/itinerary/generate", json=generate_data)
    assert generate_response.status_code == 200
    generated = generate_response.json()
    
    # Step 2: Save
    save_response = await async_client.post("/api/itinerary", json=generated)
    assert save_response.status_code == 200
    saved = save_response.json()
    
    # Step 3: Update
    update_data = {
        "destination": "Kyoto",
        "start_date": "2025-10-01", 
        "end_date": "2025-10-05",  # Shorter trip
        "interests": ["temples", "gardens"],
    }
    
    update_response = await async_client.patch(f"/api/itinerary/{saved['id']}", json=update_data)
    assert update_response.status_code == 200
    updated = update_response.json()
    
    assert updated["destination"] == "Kyoto"
    assert updated["days_count"] == 5  # Regenerated for shorter trip
    
    # Step 4: Delete
    delete_response = await async_client.delete(f"/api/itinerary/{saved['id']}")
    assert delete_response.status_code == 200
    
    # Verify it's gone
    get_response = await async_client.get("/api/itinerary")
    assert len(get_response.json()) == 0