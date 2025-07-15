from datetime import datetime

from pydantic import BaseModel, validator
from typing import Optional




class UserItineraryIn(BaseModel):
    destination: str
    start_date: str
    end_date: str
    interests: list[str]

    @validator("start_date", "end_date")
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @validator("end_date")
    def validate_end_after_start(cls, v, values):
        if "start_date" in values:
            start = datetime.strptime(values["start_date"], "%Y-%m-%d").date()
            end = datetime.strptime(v, "%Y-%m-%d").date()
            if end <= start:
                raise ValueError("End date must be after start date")
        return v


class UserItinerary(UserItineraryIn):
    id: int
    days_count: Optional[int] = None


def calculate_days(start_date_str: str, end_date_str: str) -> int:
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return (end - start).days + 1  # +1 to include both start and end days
