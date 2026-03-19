# Smart Resume Matcher - Backend API

Production-ready FastAPI backend for the Smart Resume Matcher application.

## Quick Start

### Using Docker (Recommended)

```bash
docker-compose up --build
```

API will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Manual Setup

```bash
pip install -r requirements-api.txt
uvicorn backend.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/v1/register` - Register new user
- `POST /api/v1/token` - Login and get JWT token

### Job Descriptions
- `POST /api/v1/job-descriptions` - Create new JD
- `GET /api/v1/job-descriptions` - List all JDs
- `GET /api/v1/job-descriptions/{id}` - Get specific JD
- `DELETE /api/v1/job-descriptions/{id}` - Delete JD

### Analysis
- `POST /api/v1/analyze` - Analyze text resumes
- `POST /api/v1/analyze/pdf` - Analyze PDF resumes

## Example Usage

```bash
# Register
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/token" \
  -d "username=test@example.com&password=testpass123"

# Create JD (with token)
curl -X POST "http://localhost:8000/api/v1/job-descriptions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Software Engineer","content":"Python, Django, React..."}'
```

## Database

SQLite database (`smartresume.db`) is auto-created on first run.

## Project Structure

```
backend/
├── main.py           # FastAPI application
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── database.py       # Database configuration
├── routes/
│   └── api.py        # API endpoints
└── services/
    ├── analysis.py   # Resume analysis logic
    └── auth.py       # Authentication utilities
```
