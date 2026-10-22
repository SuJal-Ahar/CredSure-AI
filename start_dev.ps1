# CredSure AI - PowerShell Startup Script
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  CredSure AI - Credit Risk Scorecard & Underwriter" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$WorkspaceRoot = $PSScriptRoot

Write-Host "[1/2] Starting CredSure FastAPI Backend on Port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkspaceRoot'; python -m uvicorn --app-dir src credsure.api.app:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting CredSure Next.js Frontend on Port 3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkspaceRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Services successfully launched!" -ForegroundColor Green
Write-Host "  Frontend Dashboard:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API Docs:    http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
