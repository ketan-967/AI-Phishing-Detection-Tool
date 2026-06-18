# 🛡️ AI Phishing Detection Tool

An AI-powered phishing detection system that combines a **machine learning backend** with a **Chrome browser extension** to flag suspicious or malicious URLs in real time, plus an early-stage **React dashboard** for manual URL checks.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![scikit-learn](https://img.shields.io/badge/scikit--learn-RandomForest-F7931E)
![Chrome Extension](https://img.shields.io/badge/Chrome%20Extension-Manifest%20V3-yellow)
![Status](https://img.shields.io/badge/status-active%20development-orange)
![License](https://img.shields.io/badge/license-unspecified-lightgrey)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Model & Dataset](#model--dataset)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project detects phishing websites by extracting features from a URL and feeding them into a trained **Random Forest classifier**. Predictions are served through a local **FastAPI** backend and consumed by a **Manifest V3 Chrome extension** that watches the active tab and warns the user when a site looks suspicious. A companion **React dashboard** is included for ad-hoc, manual URL lookups outside the browser extension.

The system is split into three independent components that share one prediction API:

1. **ML Backend** — trains and serves the phishing classifier (`train_model.py`, `app.py`).
2. **Browser Extension** — passive, real-time protection while browsing (`manifest.json`, `background.js`, `popup.html`, `popup.js`).
3. **React Dashboard** — a manual "paste a URL, get a verdict" web UI (`App.js`, `Dashboard.js`, `package.json`).

---

## Key Features

- **Real-time monitoring** — the extension listens for tab navigation events and automatically checks each new page.
- **User decisions are remembered** — once a domain is marked "Trust" or "Block," the extension skips the AI check for that domain on future visits (persisted via `chrome.storage.local`).
- **Confidence-aware verdicts** — predictions below a 70% confidence threshold are downgraded to `Suspicious` rather than a hard `Phishing`/`Legitimate` call, reducing false alarms.
- **Native browser notifications** — risky sites trigger a Chrome notification even if the popup isn't open.
- **Lightweight popup UI** — a clean status badge, animated confidence meter, and one-click Trust/Block/Reset controls.
- **Decoupled architecture** — the detection engine is a standalone REST API, so it can be reused by the extension, the dashboard, or any future client (mobile app, CLI, email scanner, etc.).

---

## Architecture

```
                ┌─────────────────────────┐
                │   dataset.csv (30 URL/   │
                │   domain features)       │
                └────────────┬─────────────┘
                             │ train_model.py
                             ▼
                ┌─────────────────────────┐
                │      model.pkl           │
                │ (RandomForestClassifier) │
                └────────────┬─────────────┘
                             │ loaded by
                             ▼
                ┌─────────────────────────┐
                │   FastAPI backend        │
                │   app.py  → /predict      │
                │   http://127.0.0.1:8000  │
                └──────┬────────────┬───────┘
                       │            │
        REST (fetch)   │            │   REST (fetch)
                       ▼            ▼
        ┌───────────────────┐  ┌───────────────────────┐
        │ Chrome Extension    │  │ React Dashboard         │
        │ background.js        │  │ App.js / Dashboard.js   │
        │ popup.html / popup.js│  │ (manual URL lookup)     │
        └───────────────────┘  └───────────────────────┘
```

The extension and the dashboard never talk to each other — both are independent clients of the same FastAPI service.

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML model | scikit-learn `RandomForestClassifier` |
| Backend API | FastAPI + Uvicorn |
| Data handling | pandas, NumPy |
| Browser extension | Chrome Extension Manifest V3 (vanilla JS) |
| Dashboard | React 18 (Create React App / `react-scripts`) |
| Automation | Windows batch script (`run_project.bat`) |

---

## Repository Structure

```
AI-Phishing-Detection-Tool/
├── app.py                # FastAPI server — loads model.pkl and exposes /predict
├── train_model.py        # Trains the RandomForest model from dataset.csv
├── dataset.csv            # Labeled phishing/legitimate URL feature dataset
├── model.pkl              # Serialized trained model (generated by train_model.py)
├── requirements.txt        # Python dependencies
├── run_project.bat         # One-click setup + run script (Windows)
│
├── manifest.json           # Chrome extension manifest (MV3)
├── background.js            # Service worker — auto-checks tabs, fires notifications
├── popup.html / popup.js     # Extension popup UI and logic
├── icon.png                  # Extension icon
│
├── App.js                    # React dashboard root component
├── Dashboard.js               # React dashboard URL-check component
├── package.json / package-lock.json   # React/Node dependencies
└── node_modules/              # Installed Node packages
```

> **Note:** `App.js` imports a component from `./components/Dashboard` and `Dashboard.js` imports a helper from `../api`. Neither a `components/` folder nor an `api.js` file currently exists in the repository — see [Known Limitations](#known-limitations).

---

## How It Works

1. **Training** (`train_model.py`): loads `dataset.csv`, drops the `index` and `Result` columns to build the feature matrix, splits 80/20 for train/test, fits a `RandomForestClassifier(n_estimators=100)`, prints accuracy, and serializes the model to `model.pkl`.
2. **Inference** (`app.py`): on each `POST /predict` call, the API receives a raw URL and computes a handful of fast, dependency-free heuristics directly from the string — URL length, presence of `https`, `@` symbols, subdomain count, and hyphens in the domain — maps them to the same 30-column schema the model was trained on (unused columns default to `0`), and returns a label plus a confidence score.
3. **Confidence gating**: if the model's top-class probability is below 70%, the verdict is reported as `Suspicious` instead of a hard `Phishing`/`Legitimate` call.
4. **Extension monitoring** (`background.js`): on every completed tab navigation, the domain is checked against locally stored user decisions; if there's no prior decision, the URL is sent to the API and a native notification fires for `Phishing` or `Suspicious` results.
5. **Popup interaction** (`popup.js`): re-runs the same check for the active tab and lets the user override the AI verdict by clicking **Trust Site** or **Block Site** — the choice is saved per-domain so the AI isn't re-queried on repeat visits, until **Reset All Settings** is used.

---

## Getting Started

### Prerequisites

- Python 3.8+ and pip
- Google Chrome (or any Chromium-based browser) for the extension
- Node.js + npm, only if you want to run the React dashboard

### 1. Clone the repository

```bash
git clone https://github.com/ketan-967/AI-Phishing-Detection-Tool.git
cd AI-Phishing-Detection-Tool
```

### 2. Set up the Python backend

**Windows (automated):**

```bash
run_project.bat
```
This creates a virtual environment, installs dependencies, and gives you a menu to either train the model or start the API server.

**Manual / cross-platform:**

```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Train the model (optional — `model.pkl` is already included)

```bash
python train_model.py
```

### 4. Start the prediction API

```bash
uvicorn app:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 5. Load the Chrome extension

1. Open `chrome://extensions`.
2. Enable **Developer mode** (top-right toggle).
3. Click **Load unpacked** and select the repository's root folder.
4. Keep the FastAPI server running in the background — the extension calls `http://127.0.0.1:8000/predict` and will fail silently if the API is offline.

### 6. (Optional) Run the React dashboard

```bash
npm install
npm start
```
> The dashboard currently requires a `src/components/Dashboard.js` and `src/api.js` to be created/relocated before it will compile — see [Known Limitations](#known-limitations).

---

## API Reference

### `POST /predict`

**Request body**
```json
{
  "url": "https://example-login-secure.com"
}
```

**Response**
```json
{
  "prediction": "Suspicious",
  "confidence": 64.21
}
```

| Field | Type | Description |
|---|---|---|
| `prediction` | string | `"Legitimate"`, `"Phishing"`, or `"Suspicious"` (low-confidence fallback) |
| `confidence` | number | Model's top-class probability, as a percentage |

CORS is currently open to all origins (`allow_origins=["*"]`) to support both the extension and the dashboard during local development.

---

## Model & Dataset

- **Algorithm:** `RandomForestClassifier` (100 estimators, scikit-learn)
- **Feature schema:** 30 attributes describing URL structure, domain registration, HTML/JS behavior, and abnormal-request patterns (e.g. `having_IPhaving_IP_Address`, `SSLfinal_State`, `age_of_domain`, `Iframe`, `Abnormal_URL`, `web_traffic`).
- **Labels:** binary phishing vs. legitimate (`Result` column), with confidence-based "Suspicious" introduced only at inference time.
- **Reported accuracy:** printed to the console during training (`accuracy_score`) and will vary run-to-run with the random train/test split — no fixed number is hard-coded in this README to avoid going stale.

---

## Known Limitations

These are worth knowing before relying on this in production:

- **Partial feature coverage at inference time.** The model is trained on all 30 dataset columns, but `app.py` only computes 5 of them live from the URL string; the remaining 25 (e.g. domain age, WHOIS data, page rank, web traffic) default to `0`. This can meaningfully reduce real-world accuracy compared to the offline test metrics.
- **`python-whois` is listed but unused.** It's in `requirements.txt`, presumably intended for richer domain-age/registration features, but no current code path calls it.
- **Hard-coded localhost endpoint.** Both the extension and the dashboard call `http://127.0.0.1:8000` directly — the extension only works while you are running the API locally, and it currently can't be pointed at a remote/production deployment without editing source.
- **React dashboard is not fully wired.** `App.js` expects `./components/Dashboard`, and `Dashboard.js` expects `../api`; neither path exists in the current repository layout, so `npm start` will fail until those are added or the imports are corrected.
- **No authentication on the API.** Anyone with network access to the host can call `/predict`.
- **No automated tests or CI pipeline** currently exist for the model, the API, or the extension logic.
- **No LICENSE file** is present in the repository — see [License](#license).

---

## Roadmap

- [ ] Implement full 30-feature live extraction (WHOIS lookups, SSL certificate inspection, domain age, redirect chains) to close the train/inference feature gap.
- [ ] Move the API base URL into a config value (env variable or extension options page) instead of hard-coding `127.0.0.1:8000`.
- [ ] Finish wiring the React dashboard (`src/` layout, `api.js` helper, routing).
- [ ] Add request validation/auth (API key or local-only binding) before any non-local deployment.
- [ ] Add unit tests for feature extraction and an integration test for `/predict`.
- [ ] Containerize the backend (Dockerfile) for reproducible deployment.
- [ ] Add a GitHub Actions workflow for linting/tests on push.
- [ ] Publish the extension to the Chrome Web Store once the endpoint is configurable.
- [ ] Add a `LICENSE` file.

---

## Security Notes

- Treat predictions as **advisory, not authoritative** — this is a heuristic + ML classifier, not a substitute for browser-native phishing protection or enterprise security tooling.
- Because the API currently runs unauthenticated on `localhost`, do not expose it on a public interface without adding authentication and HTTPS.
- The extension requests broad `tabs`/`activeTab` permissions to monitor navigation — review `manifest.json` before distributing it to others.

---

## Contributing

Contributions are welcome. A good first step is picking up one of the [Roadmap](#roadmap) items, especially closing the feature-extraction gap or wiring up the dashboard. Please open an issue describing the change before submitting a large pull request.

---

## License

No license is currently published for this repository. Until one is added, all rights are reserved by the author by default — if you intend to reuse, modify, or distribute this code, reach out to the repository owner or wait for a `LICENSE` file (MIT is a common, permissive choice for projects like this) to be added.
