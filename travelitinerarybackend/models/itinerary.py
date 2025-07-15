from datetime import datetime

from typing import Optional
from pydantic import BaseModel, field_validator




class UserItineraryIn(BaseModel):
    destination: str
    start_date: str
    end_date: str
    interests: list[str]

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @field_validator("end_date")
    @classmethod
    def validate_end_after_start(cls, v, info):
        if info.data and "start_date" in info.data:
            start = datetime.strptime(info.data["start_date"], "%Y-%m-%d").date()
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
