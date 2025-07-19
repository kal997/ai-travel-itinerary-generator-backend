FROM python:3.12.3-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run uses PORT environment variable (default 8080)
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the app with dynamic port support using sh -c for var expansion
CMD sh -c 'uvicorn travelitinerarybackend.main:app --host 0.0.0.0 --port ${PORT:-8080}'
