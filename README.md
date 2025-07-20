# AI Travel Itinerary Generator - Backend

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An intelligent travel itinerary generator backend powered by Google's Gemini AI. This FastAPI-based service provides APIs for creating personalized travel plans based on user preferences, destinations, and interests.

## 🚀 Features

- **AI-Powered Itinerary Generation**: Leverages Google Gemini 2.5 Flash for intelligent travel planning
- **User Authentication**: JWT-based authentication with secure password hashing (Argon2)
- **RESTful API**: Clean, well-documented API endpoints
- **PostgreSQL Database**: Robust data persistence with async database operations
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Cloud-Ready**: Configured for Google Cloud Run deployment
- **Logging & Monitoring**: Structured logging with correlation IDs

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Deployment](#deployment)
- [Limitations & Known Issues](#limitations--known-issues)

## 🔧 Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Google Cloud Project with Vertex AI enabled
- Docker & Docker Compose (optional)

## 📁 Project Structure

```
travelitinerarybackend/
├── alembic/                 # Database migrations
├── travelitinerarybackend/
│   ├── models/             # Pydantic models
│   │   ├── user.py
│   │   └── itinerary.py
│   ├── routers/            # API endpoints
│   │   ├── user.py
│   │   └── itinerary.py
│   ├── services/           # Business logic
│   │   └── gemini_service.py
│   ├── tests/              # Test suite
│   ├── config.py           # Configuration management
│   ├── database.py         # Database setup
│   ├── security.py         # Authentication logic
│   └── main.py            # Application entry point
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── docker-compose.yml      # Local development setup
├── Dockerfile             # Production container
└── .env.example           # Environment variables template
```

## 🚀 Getting Started

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd travelitinerarybackend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn travelitinerarybackend.main:app --reload
   ```

### Docker Development Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start a PostgreSQL database
   - Run database migrations
   - Start the FastAPI application on port 8000

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Environment state
ENV_STATE=dev  # dev, prod, or test

# Development Configuration
DEV_DATABASE_URL=postgresql://user:password@localhost/travel_itinerary
DEV_SECRET_KEY=your-secret-key-here
DEV_ALGORITHM=HS256
DEV_GCP_PROJECT_ID=your-gcp-project-id
DEV_GCP_REGION=us-central1

# Production Configuration
PROD_DATABASE_URL=postgresql://user:password@host/dbname
PROD_SECRET_KEY=your-production-secret-key
PROD_ALGORITHM=HS256
PROD_GCP_PROJECT_ID=your-production-gcp-project
PROD_GCP_REGION=us-central1
```

### Google Cloud Configuration

1. **Enable Vertex AI API** in your GCP project
2. **Create a service account** with Vertex AI User role
3. **Download service account key** and set path:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
   ```

## 📚 API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Authentication Endpoints

#### Register User
```http
POST /register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Login
```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword&grant_type=password
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Itinerary Endpoints

All itinerary endpoints require authentication. Include the token in headers:
```http
Authorization: Bearer <your-access-token>
```

#### Generate Itinerary (Preview)
```http
POST /api/itinerary/generate
Content-Type: application/json

{
  "destination": "Paris",
  "start_date": "2025-08-01",
  "end_date": "2025-08-10",
  "interests": ["food", "art", "history"]
}
```

Response:
```json
{
  "days_count": 10,
  "itinerary": [
    {
      "day": 1,
      "activities": [
        "Visit the Eiffel Tower",
        "Lunch at a bistro",
        "Evening Seine river cruise"
      ]
    }
  ]
}
```

#### Save Itinerary
```http
POST /api/itinerary
Content-Type: application/json

{
  "destination": "Paris",
  "start_date": "2025-08-01",
  "end_date": "2025-08-10",
  "days_count": 10,
  "interests": ["food", "art"],
  "generated_itinerary": [...]
}
```

#### Get All Itineraries
```http
GET /api/itinerary
```

#### Update Itinerary
```http
PATCH /api/itinerary/{id}
Content-Type: application/json

{
  "destination": "Rome",
  "start_date": "2025-09-01",
  "end_date": "2025-09-05",
  "days_count": 5,
  "interests": ["history", "food"],
  "generated_itinerary": [...]
}
```

#### Delete Itinerary
```http
DELETE /api/itinerary/{id}
```

### Health Check
```http
GET /health
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Itineraries Table
```sql
CREATE TABLE itineraries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    destination VARCHAR NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count INTEGER NOT NULL,
    interests JSON NOT NULL,  -- Array of strings
    generated_itinerary JSON NOT NULL,  -- Full AI response
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=travelitinerarybackend

# Run specific test file
pytest travelitinerarybackend/tests/test_security.py
```

### Test Structure
- `conftest.py`: Test fixtures and configuration
- `test_security.py`: Authentication and security tests
- `test_itinerary.py`: Itinerary API tests

## 🚢 Deployment

### Google Cloud Run Deployment

1. **Build and push Docker image**
   ```bash
   # Build image
   docker build -t gcr.io/YOUR_PROJECT_ID/travel-backend .
   
   # Push to Container Registry
   docker push gcr.io/YOUR_PROJECT_ID/travel-backend
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy travel-backend \
     --image gcr.io/YOUR_PROJECT_ID/travel-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENV_STATE=prod
   ```

3. **Set up Cloud SQL** (if using managed PostgreSQL)
   - Create Cloud SQL instance
   - Update PROD_DATABASE_URL with connection string

### Docker Production Build

```bash
# Build production image
docker build -f Dockerfile -t travel-backend:latest .

# Run container
docker run -p 8080:8080 \
  -e ENV_STATE=prod \
  -e PROD_DATABASE_URL=your-db-url \
  -e PROD_SECRET_KEY=your-secret \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v /path/to/credentials.json:/app/credentials.json \
  travel-backend:latest
```

## 🔍 Gemini Studio Integration

The application integrates with Google's Vertex AI Gemini model for itinerary generation:

### Configuration
- Model: `gemini-2.5-flash`
- Region: Configurable via `GCP_REGION`
- Authentication: Service account with Vertex AI User role

### Prompt Engineering
The service uses a structured prompt to generate JSON-formatted itineraries:
- Input: destination, dates, interests
- Output: Day-by-day activity recommendations
- Format: Structured JSON for easy parsing

### Usage Limits
- Subject to Vertex AI quotas and pricing
- Recommended to implement caching for repeated queries
- Consider rate limiting for production use

## ⚠️ Limitations & Known Issues

### Current Limitations

1. **No Caching**: Generated itineraries are not cached, leading to API calls for identical requests
2. **Basic Error Handling**: Gemini API errors could be more gracefully handled
3. **Limited Validation**: Minimal validation on destination names
4. **No Pagination**: Itinerary list endpoint returns all records

### Known Issues
- None

### Planned Improvements

- [ ] Implement Redis caching for generated itineraries
- [ ] Add pagination to list endpoints
- [ ] Support for collaborative itineraries
- [ ] Export itineraries to various formats (PDF, iCal)
- [ ] Multi-language support
- [ ] Real-time itinerary sharing
- [ ] Integration with booking APIs
- [ ] Budget estimation features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation as needed
- Use conventional commits format

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues before creating new ones
- Provide detailed reproduction steps for bugs

---

## Technology Stack

- **Framework**: FastAPI
- **AI Model**: Google Gemini 2.5 Flash (Vertex AI)
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: JWT with OAuth2
- **Container**: Docker
- **Cloud Platform**: Google Cloud Platform (Cloud Run, Vertex AI)