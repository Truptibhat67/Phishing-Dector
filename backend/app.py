from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from model import URLModel, ensure_model
import os
import json
from pathlib import Path
from datetime import datetime
import multiprocessing
multiprocessing.freeze_support()

# In-memory user storage (for demo purposes)
users: Dict[str, Dict[str, str]] = {}


app = FastAPI(title="Phishing URL Detector", version="1.0.0")

# 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["detectoeapp.netlify.app","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url_model: URLModel = ensure_model()

METRICS_PATH = Path(__file__).parent / "metrics.json"

def load_metrics():
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text())
    return {"total": 0, "phishing": 0, "legit": 0, "last_updated": None}

def save_metrics(metrics: Dict[str, Any]):
    metrics["last_updated"] = datetime.utcnow().isoformat()
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

class PredictIn(BaseModel):
    url: str

class PredictOut(BaseModel):
    url: str
    pred_label: str
    pred_proba: float
    features: Dict[str, Any]
    top_contributors: List[Dict[str, Any]]

class SignupRequest(BaseModel):
    username: str
    password: str
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return load_metrics()

@app.post("/predict", response_model=PredictOut)
def predict(payload: PredictIn):
    url = payload.url.strip()
    result = url_model.predict_with_explain(url)
    # Update metrics
    m = load_metrics()
    m["total"] += 1
    if result["pred_label"] == "phishing":
        m["phishing"] += 1
    else:
        m["legit"] += 1
    save_metrics(m)
    return PredictOut(**result)

@app.post("/api/auth/signup")
def signup(payload: SignupRequest):
    if payload.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    users[payload.username] = {
        "password": payload.password,
        "email": payload.email
    }
    return {"message": "User registered successfully"}

@app.post("/api/auth/login")
def login(payload: LoginRequest):
    user = users.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful"}

@app.post("/api/auth/logout")
def logout():
    return {"message": "Logout successful"}
