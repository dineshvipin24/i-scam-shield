@echo off
echo ============================================
echo   CAMP PROTECT - AI VOICE DETECTION SETUP
echo ============================================
echo.

echo [1/3] Installing ML dependencies...
pip install xgboost lightgbm joblib scikit-learn numpy scipy --quiet
if %errorlevel% neq 0 (
    echo [WARN] Some packages may have failed. Continuing...
)
echo [1/3] Done.

echo.
echo [2/3] Training AI Voice Detection model...
cd /d "%~dp0backend\model"
python train_voice_model.py
if %errorlevel% neq 0 (
    echo [ERROR] Training failed!
    pause
    exit /b 1
)
echo [2/3] Done.

echo.
echo [3/3] Starting backend server...
cd /d "%~dp0backend"
echo Server starting at http://localhost:8000
echo Press Ctrl+C to stop.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
