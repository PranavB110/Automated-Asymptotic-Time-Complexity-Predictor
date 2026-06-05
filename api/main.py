import sys
sys.path.append("D:\\complexity-predictor")

import joblib
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from feature_extraction.multi_extractor import extract_features_multilang

# ── Load model artifacts ──────────────────────────────────────────────────────
model         = joblib.load("model/model.pkl")
le            = joblib.load("model/label_encoder.pkl")
feature_names = joblib.load("model/feature_names.pkl")

app = FastAPI(title="Time Complexity Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/charts", StaticFiles(directory="report"), name="charts")

class CodeInput(BaseModel):
    code: str
    language: str = "auto"

@app.get("/")
def root():
    return {"message": "Time Complexity Predictor API is running ✅"}

@app.post("/predict")
def predict(payload: CodeInput):
    result = extract_features_multilang(payload.code, payload.language)
    if result is None or result[0] is None:
        return {"error": "Could not parse code. Check for syntax errors."}

    features, detected_language = result
    X          = np.array([list(features.values())])
    prediction = model.predict(X)[0]
    proba      = model.predict_proba(X)[0]
    label      = le.inverse_transform([prediction])[0]
    confidence = round(float(proba.max()) * 100, 2)

    all_probs = {
        le.inverse_transform([i])[0]: round(float(p) * 100, 2)
        for i, p in enumerate(proba)
    }

    return {
        "complexity":        label,
        "confidence":        confidence,
        "all_probabilities": all_probs,
        "features":          features,
        "detected_language": detected_language,
    }

@app.get("/charts-list")
def charts_list():
    return {
        "charts": [
            {"name": "Confusion Matrix",   "url": "http://127.0.0.1:8000/charts/confusion_matrix.png"},
            {"name": "Feature Importance", "url": "http://127.0.0.1:8000/charts/feature_importance.png"},
            {"name": "Class Distribution", "url": "http://127.0.0.1:8000/charts/class_distribution.png"},
            {"name": "Model Comparison",   "url": "http://127.0.0.1:8000/charts/model_comparison.png"},
        ]
    }

@app.get("/health")
def health():
    return {
        "status":             "ok",
        "model":              "Random Forest",
        "classes":            list(le.classes_),
        "supported_languages": ["python", "javascript", "java", "cpp"]
    }