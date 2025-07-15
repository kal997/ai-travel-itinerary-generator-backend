from fastapi import FastAPI

from travelitinerarybackend.routers.itinerary import router as itinerary_router

app = FastAPI()
app.include_router(itinerary_router, prefix="/api")
