# Phishing URL Dector

Full-stack app to detect phishing URLs with ML predictions.

- Frontend: React
- Backend: FastAPI


## Prerequisites
- Node.js v16+ and npm
- Python 3.9+ and pip

## Steps to run the project locally

### Backend Setup

- Navigate to backend folder:
  cd backend

- Create virtual environment (optional):
  python -m venv venv
  venv\Scripts\activate      

- Install dependencies:
  pip install -r requirements.txt

- Run FastAPI server:
  uvicorn main:app --reload --port 8000

- Backend URL: http://localhost:8000


### Frontend Setup

- Navigate to frontend folder:
  cd frontend

- Install dependencies:
  npm install

- Run development server:
  npm run dev

Frontend URL: http://localhost:3000

Ensure backend is running for API calls to work.


## Architecture

### Frontend (React)
- Users enter a URL in a large text input.
- On submit, calls `predictURL(url)` API.
- Displays prediction: ✅ Safe / ❌ Phishing, confidence, and optional features.
- Dashboard shows aggregated metrics.

### Backend (FastAPI)
- Handles prediction using ML model (`URLModel`).
- Updates metrics after each prediction.
- Supports health check and metrics endpoints.

