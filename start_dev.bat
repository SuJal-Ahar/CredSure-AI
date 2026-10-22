@echo off
echo ========================================================
echo   CredSure AI - Credit Risk Scorecard & Underwriter
echo ========================================================
echo.

echo [1/2] Launching CredSure FastAPI Backend (Port 8000)...
start "CredSure AI - Backend" cmd /k "python -m uvicorn --app-dir src credsure.api.app:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo [2/2] Launching CredSure Next.js Frontend Dashboard (Port 3000)...
start "CredSure AI - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   Services are running!
echo   Frontend Dashboard:  http://localhost:3000
echo   Backend API Docs:    http://127.0.0.1:8000/docs
echo ========================================================
echo.
