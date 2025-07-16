import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from travelitinerarybackend.database import database, itinerary_table
from travelitinerarybackend.models.itinerary import (
    SaveItineraryRequest,
    UserItinerary,
    UserItineraryIn,
    calculate_days,
)
from travelitinerarybackend.models.user import User
from travelitinerarybackend.security import get_current_user
from travelitinerarybackend.services.gemini_service import (
    GeminiService,
    get_gemini_service,
)

router = APIRouter()

logger = logging.getLogger(__name__)


def convert_dates_to_strings(record_dict):
    """Helper function to convert date objects to strings"""
    if "start_date" in record_dict and record_dict["start_date"]:
        record_dict["start_date"] = record_dict["start_date"].strftime("%Y-%m-%d")
    if "end_date" in record_dict and record_dict["end_date"]:
        record_dict["end_date"] = record_dict["end_date"].strftime("%Y-%m-%d")
    return record_dict


# Save a new itinerary
@router.post("/itinerary", response_model=UserItinerary)
async def create_itinerary(
    request: SaveItineraryRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Save the generated itinerary to database.
    Called after user approves the generated preview.
    """
    try:
        # Convert string dates to Date objects
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()

        # Prepare data for database
        save_data = {
            "destination": request.destination,
            "start_date": start_date,
            "end_date": end_date,
            "days_count": request.days_count,
            "interests": request.interests,
            "generated_itinerary": request.itinerary,
        }

        # Save to database
        query = itinerary_table.insert().values(**save_data, user_id=current_user.id)
        last_record_id = await database.execute(query)

        # Fetch the saved record
        fetch_query = itinerary_table.select().where(
            itinerary_table.c.id == last_record_id
        )
        saved_record = await database.fetch_one(fetch_query)

        # Convert Date objects back to strings for response
        response_data = dict(saved_record)
        response_data = convert_dates_to_strings(response_data)
        logger.info(f"Saved itinerary: {response_data}")
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving itinerary: {str(e)}")


# Get all itineraries
@router.get("/itinerary", response_model=list[UserItinerary])
async def get_itineraries(current_user: Annotated[User, Depends(get_current_user)]):
    try:
        query = itinerary_table.select()
        results = await database.fetch_all(query)

        # Convert Date objects to strings for all records
        converted_results = []
        for row in results:
            row_dict = dict(row)
            row_dict = convert_dates_to_strings(row_dict)
            converted_results.append(row_dict)

        return converted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Delete a saved itinerary
@router.delete("/itinerary/{id}")
async def delete_itinerary(
    id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        # First, check if the record exists
        check_query = itinerary_table.select().where(itinerary_table.c.id == id)
        existing_record = await database.fetch_one(check_query)

        if not existing_record:
            raise HTTPException(status_code=404, detail="Itinerary not found")

        # If exists, delete it
        delete_query = itinerary_table.delete().where(itinerary_table.c.id == id)
        await database.execute(delete_query)

        return {"message": f"Itinerary {id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.patch("/itinerary/{id}", response_model=UserItinerary)
async def update_itinerary(
    id: int,
    updates: UserItineraryIn,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Update itinerary - always regenerates with new parameters
    Same input as generate endpoint
    """
    try:
        # Check if exists
        check_query = itinerary_table.select().where(itinerary_table.c.id == id)
        existing = await database.fetch_one(check_query)
        if not existing:
            raise HTTPException(status_code=404, detail="Itinerary not found")

        # Call generate endpoint with new parameters
        generated_response = await generate_itinerary(updates, current_user)

        # Convert dates for database
        start_date_obj = datetime.strptime(updates.start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(updates.end_date, "%Y-%m-%d").date()

        # Update database with regenerated data
        update_data = {
            "destination": updates.destination,
            "start_date": start_date_obj,
            "end_date": end_date_obj,
            "days_count": generated_response["days_count"],
            "interests": updates.interests,
            "generated_itinerary": generated_response["itinerary"],
        }

        update_query = (
            itinerary_table.update()
            .where(itinerary_table.c.id == id)
            .values(**update_data)
        )
        await database.execute(update_query)

        # Return updated record
        fetch_query = itinerary_table.select().where(itinerary_table.c.id == id)
        updated_record = await database.fetch_one(fetch_query)
        response_data = dict(updated_record)
        response_data = convert_dates_to_strings(response_data)

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Generate itinerary
@router.post("/itinerary/generate")
async def generate_itinerary(
    request: UserItineraryIn,
    gemini_service: Annotated[GeminiService, Depends(get_gemini_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Generate itinerary for preview - NO database save.
    User can review before deciding to save.
    """
    try:
        days_count = calculate_days(request.start_date, request.end_date)

        # Generate actual itinerary
        generated_itinerary = gemini_service.generate_itinerary(
            request.destination, request.start_date, request.end_date, request.interests
        )
        return {"days_count": days_count, "itinerary": generated_itinerary}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating itinerary: {str(e)}"
        )
