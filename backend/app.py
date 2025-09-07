from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from model import URLModel, ensure_model
import os
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Phishing URL Detector", version="1.0.0")

# 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
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
