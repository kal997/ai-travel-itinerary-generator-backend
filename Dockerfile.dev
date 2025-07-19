FROM python:3.12.3-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run migrations then start the app
CMD ["sh", "-c", "alembic upgrade head && uvicorn travelitinerarybackend.main:app --host 0.0.0.0 --port 8000"]