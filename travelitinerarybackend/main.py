import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from travelitinerarybackend.database import database
from travelitinerarybackend.logging_conf import configure_logging
from travelitinerarybackend.routers.itinerary import router as itinerary_router
from travelitinerarybackend.routers.user import router as user_router

logger = logging.getLogger(__name__)


# conext manager to do setup and teardown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup
    configure_logging()
    await database.connect()
    yield
    # teardown
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "https://ai-travel-itinerary-gen-app-frontend-181459384771.us-central1.run.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(itinerary_router, prefix="/api")
app.include_router(user_router)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
