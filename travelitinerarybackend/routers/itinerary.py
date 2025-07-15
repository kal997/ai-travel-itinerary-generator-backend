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
