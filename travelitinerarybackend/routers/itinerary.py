from fastapi import APIRouter

from travelitinerarybackend.models.itinerary import UserItinerary, UserItineraryIn

router = APIRouter()


itineraries_table = {}


# save itinerary in a simple dict
@router.post("/itinerary/", response_model=UserItinerary)
async def create_itinerary(user_itinerary: UserItineraryIn):
    data = user_itinerary.dict()
    new_id = len(itineraries_table) + 1
    new_itinerary = UserItinerary(**data, id=new_id)
    itineraries_table[new_id] = new_itinerary
    return new_itinerary


# get all itineraries
@router.get("/itinerary/", response_model=list[UserItinerary])
async def get_itinerary():
    return itineraries_table.values()
    