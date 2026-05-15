# BabyBloom

A full-stack application for baby growth tracking and medical management.

## Project Structure

- **`backend/`**: Django project and apps.
  - Run commands from this directory: `python manage.py runserver`
- **`frontend/`**: React application built with Vite.
  - Run commands from this directory: `npm run dev`

## Getting Started

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py runserver`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Environment Configuration

Both the backend and frontend use environment variables for configuration.

### Backend (backend/.env)
- SECRET_KEY: Django secret key.
- DEBUG: Set to True for development.
- ALLOWED_HOSTS: Comma-separated list of allowed hosts.
- CORS_ALLOWED_ORIGINS: Comma-separated list of frontend URLs.

### Frontend (frontend/.env)
- VITE_API_URL: URL of the backend API (e.g., http://127.0.0.1:8000).
