from pydantic import BaseModel


class UserItineraryIn(BaseModel):
    destination: str
    start_date: str
    end_date: str
    interests: list[str]


class UserItinerary(UserItineraryIn):
    id: int
