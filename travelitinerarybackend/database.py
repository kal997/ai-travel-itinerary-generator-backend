import databases
import sqlalchemy

from travelitinerarybackend.config import config

metadata = sqlalchemy.MetaData()

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=sqlalchemy.func.now()),
)

itinerary_table = sqlalchemy.Table(
    "itineraries",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=True),
    sqlalchemy.Column("destination", sqlalchemy.String),
    sqlalchemy.Column("start_date", sqlalchemy.Date),
    sqlalchemy.Column("end_date", sqlalchemy.Date),
    sqlalchemy.Column("days_count", sqlalchemy.Integer),
    sqlalchemy.Column("interests", sqlalchemy.JSON),  # ["art", "food"]
    sqlalchemy.Column("generated_itinerary", sqlalchemy.JSON),  # Full Gemini response
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=sqlalchemy.func.now()),
)

engine = sqlalchemy.create_engine(config.DATABASE_URL)
metadata.create_all(engine)

database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)
