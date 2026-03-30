@echo off
title Phishing Detection System
echo ---------------------------------------
echo Checking Environment and Starting...
echo ---------------------------------------

:: 1. Check if venv exists, if not, create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: 2. Activate venv
call venv\Scripts\activate

:: 3. Update pip and install requirements quietly
echo Updating dependencies...
python -m pip install --upgrade pip >nul
pip install pandas numpy scikit-learn fastapi uvicorn python-whois >nul

:: 4. Choose what to run
echo ---------------------------------------
echo 1. Train Model
echo 2. Start API Server
echo ---------------------------------------
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    python train_model.py
    pause
) else (
    echo Starting FastAPI Server at http://127.0.0.1:8000
    uvicorn app:app --reload
)

pause