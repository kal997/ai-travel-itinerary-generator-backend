from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserItineraryIn(BaseModel):
    destination: str
    start_date: str
    end_date: str
    interests: list[str]


class UserItinerary(UserItineraryIn):
    id: int


itineraries_table = {}


# save itinerary in a simple dict
@app.post("/api/itinerary/", response_model=UserItinerary)
async def create_itinerary(user_itinerary: UserItineraryIn):
    data = user_itinerary.dict()
    new_id = len(itineraries_table) + 1
    new_itinerary = UserItinerary(**data, id=new_id)
    itineraries_table[new_id] = new_itinerary
    return new_itinerary


@app.get("/api/itinerary/", response_model=list[UserItinerary])
async def get_itinerary():
    return itineraries_table.values()


@app.get("/")
async def root():
    return {"message": "Hello World"}
