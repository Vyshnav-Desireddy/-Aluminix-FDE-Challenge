# Aluminix - Sales Inbox Task Router

## Overview

This is the Alumnx AI Labs FDE Intern Hiring Challenge project: "The Sales Inbox → Task Router". The system accepts messy sales emails, classifies them using Gemini AI, routes them to the correct team member, creates/update persistent tasks, and provides a React frontend for task management.

## Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **AI**: Google Gemini API
- **Frontend**: React + Vite
- **Styling**: Tailwind CSS

## Architecture

- Browser never calls Gemini directly
- Browser never calls the raw Task API directly
- Gemini is only called from the backend
- All backend routes are available under one backend base URL
- Data persists across server restarts using PostgreSQL
- Environment variables are used for all secrets

## Project Structure

```
Aluminix/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration using environment variables
│   │   ├── database.py          # Database connection and session management
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   └── base.py          # Base model with common fields
│   │   ├── schemas/             # Pydantic schemas for request/response
│   │   │   ├── __init__.py
│   │   │   └── base.py          # Base schema with common fields
│   │   ├── api/                 # API route handlers
│   │   │   ├── __init__.py
│   │   │   └── health.py        # Health check endpoint
│   │   ├── services/            # Business logic layer
│   │   │   ├── __init__.py
│   │   │   └── base.py          # Base service class
│   │   ├── repositories/        # Data access layer
│   │   │   ├── __init__.py
│   │   │   └── base.py          # Base repository class
│   │   ├── utils/               # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── logging.py       # Structured logging setup
│   │   │   └── exceptions.py    # Custom exception classes
│   │   └── tests/               # Test files
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # Main React component
│   │   └── index.css            # Tailwind CSS imports
│   ├── public/                  # Static assets
│   ├── index.html               # HTML template
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── tailwind.config.js       # Tailwind CSS configuration
│   └── postcss.config.js        # PostCSS configuration
├── docs/                        # Documentation
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

6. Edit `.env` with your actual values:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `CANDIDATE_ID`: Your email address (normalized to lowercase)
   - `FRONTEND_URL`: Your frontend URL (e.g., `http://localhost:5173`)

7. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Planned Backend Routes

### Task API
- `POST /tasks` - Create a new task
- `PATCH /tasks/{task_id}` - Update a task
- `GET /tasks` - List all tasks
- `DELETE /tasks/{task_id}` - Delete a task
- `GET /users` - List users

### Application API
- `POST /ingest` - Ingest and classify sales emails
- `GET /api/tasks` - Get tasks for the dashboard
- `GET /api/stats` - Get statistics
- `POST /api/chat` - Grounded chat API

## Health Check

The backend includes a health check endpoint:
- `GET /health` - Returns application status and version

## Development Notes

- All tasks must include `candidate_id` (normalized to lowercase and trimmed)
- The architecture follows clean separation: API → Services → Repositories → Models
- Type hints are used throughout the codebase
- Pydantic models for data validation
- Structured logging is configured
- Custom exception handling with appropriate HTTP status codes
- CORS is configured for local development and production

## Deployment Targets

- **Backend**: Render
- **Frontend**: Vercel
- **Database**: Supabase/PostgreSQL
