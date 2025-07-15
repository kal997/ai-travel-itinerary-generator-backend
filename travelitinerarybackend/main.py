from contextlib import asynccontextmanager

from fastapi import FastAPI

from travelitinerarybackend.database import database
from travelitinerarybackend.routers.itinerary import router as itinerary_router


# conext manager to do setup and teardown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup
    await database.connect()
    yield
    # teardown
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(itinerary_router, prefix="/api")
