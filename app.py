from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd

app = FastAPI()

# The CORS middleware must be added before any routes are defined.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Load the trained machine learning model.
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Error: model.pkl not found. Please run train_model.py first.")
    model = None

# Define the data model for the incoming request body.
class URLRequest(BaseModel):
    features: list

# Define API endpoints.
@app.get("/")
def root():
    return {"message": "Phishing Detection API is running"}

@app.post("/predict")
def predict(request: URLRequest):
    if model is None:
        return {"error": "Model not loaded."}
    
    df = pd.DataFrame([request.features])
    prediction = model.predict(df)[0]
    result = "Phishing" if prediction == -1 else "Legitimate"
    
    return {"prediction": result}