from fastapi import APIRouter, HTTPException

from travelitinerarybackend.models.itinerary import (
    UserItinerary,
    UserItineraryIn,
    calculate_days,
)

router = APIRouter()


itineraries_table = {}


# Save a new itinerary
@router.post("/itinerary", response_model=UserItinerary)
async def create_itinerary(user_itinerary: UserItineraryIn):
    try:
        data = user_itinerary.dict()
        new_id = len(itineraries_table) + 1
        days_count = calculate_days(data["start_date"], data["end_date"])

        new_itinerary = UserItinerary(**data, id=new_id, days_count=days_count)
        itineraries_table[new_id] = new_itinerary
        return new_itinerary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get all itineraries
@router.get("/itinerary", response_model=list[UserItinerary])
async def get_itineraries():
    return list(itineraries_table.values())


# Delete a saved itinerary
@router.delete("/itinerary/{id}")
async def delete_itinerary(id: int):
    if id not in itineraries_table:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    deleted_itinerary = itineraries_table.pop(id)
    return {"message": f"Itinerary {deleted_itinerary} deleted successfully"}


# Modify a saved itinerary
@router.patch("/itinerary/{id}", response_model=UserItinerary)
async def update_itinerary(id: int, updates: UserItineraryIn):
    if id not in itineraries_table:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    try:
        # Update the itinerary with new data
        update_data = updates.dict()
        days_count = calculate_days(update_data["start_date"], update_data["end_date"])

        updated_itinerary = UserItinerary(**update_data, id=id, days_count=days_count)
        itineraries_table[id] = updated_itinerary
        return updated_itinerary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Generate itinerary (placeholder without Gemini)
@router.post("/itinerary/generate")
async def generate_itinerary(request: UserItineraryIn):
    try:
        days_count = calculate_days(request.start_date, request.end_date)

        # simulatee gemini response with hardcoded activities
        itinerary = []
        for day in range(1, days_count + 1):

            itinerary.append(
                {
                    "day": day,
                    "activities": [
                        "Visit the Louvre",
                        "Lunch at Le Comptoir",
                        "Evening Seine cruise",
                    ],
                }
            )

        return {"itinerary": itinerary}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
