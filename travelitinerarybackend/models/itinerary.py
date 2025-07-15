from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class UserItineraryIn(BaseModel):
    """Base model for user input when generating/updating an itinerary"""

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
            if end < start:
                raise ValueError("End date must be after start date")
        return v


class SaveItineraryRequest(UserItineraryIn):
    """Model for saving generated itinerary to database"""

    days_count: int
    itinerary: list[dict]  # The generated itinerary data


class UserItinerary(UserItineraryIn):
    """Model for itinerary stored in database"""

    id: int
    days_count: int
    generated_itinerary: Optional[list[dict]] = None
    created_at: datetime


def calculate_days(start_date_str: str, end_date_str: str) -> int:
    """Calculate number of days between start and end dates (inclusive)"""
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return (end - start).days + 1
