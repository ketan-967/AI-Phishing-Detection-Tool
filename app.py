from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    model = None

COLUMNS = [
    'having_IPhaving_IP_Address', 'URLURL_Length', 'Shortining_Service',
    'having_At_Symbol', 'double_slash_redirecting', 'Prefix_Suffix',
    'having_Sub_Domain', 'SSLfinal_State', 'Domain_registeration_length',
    'Favicon', 'port', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor',
    'Links_in_tags', 'SFH', 'Submitting_to_email', 'Abnormal_URL',
    'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe',
    'age_of_domain', 'DNSRecord', 'web_traffic', 'Page_Rank', 'Google_Index',
    'Links_pointing_to_page', 'Statistical_report'
]

class URLRequest(BaseModel):
    url: str # We receive the raw URL now for better extraction

@app.post("/predict")
def predict(request: URLRequest):
    if model is None: return {"error": "Model missing"}
    
    url = request.url
    
    # --- Feature Extraction Logic (-1, 0, 1) ---
    features = {col: 0 for col in COLUMNS}
    
    # URL Length
    features['URLURL_Length'] = -1 if len(url) > 75 else (0 if len(url) > 54 else 1)
    # HTTPS
    features['SSLfinal_State'] = 1 if url.startswith('https') else -1
    # @ Symbol
    features['having_At_Symbol'] = -1 if '@' in url else 1
    # Dots (Subdomains)
    dots = url.split('//')[-1].count('.')
    features['having_Sub_Domain'] = -1 if dots > 3 else (0 if dots == 3 else 1)
    # Prefix/Suffix (Dash in domain)
    features['Prefix_Suffix'] = -1 if '-' in url.split('/')[2] else 1

    df = pd.DataFrame([features], columns=COLUMNS)
    
    # Get prediction and confidence
    prediction = model.predict(df)[0]
    probabilities = model.predict_proba(df)[0]
    confidence = max(probabilities)

    # Determine Result based on Confidence
    if confidence < 0.70: # If model is less than 70% sure
        result = "Suspicious"
    else:
        result = "Phishing" if prediction == -1 else "Legitimate"

    return {"prediction": result, "confidence": round(confidence * 100, 2)}