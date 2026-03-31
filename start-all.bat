@echo off
REM FraudShield AI - Start All Services (Windows)

echo ======================================================================
echo FraudShield AI - Starting All Services
echo ======================================================================
echo.

REM Start Backend
echo Starting Backend Server...
start "FraudShield Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend
echo Starting Frontend...
start "FraudShield Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ======================================================================
echo All services started!
echo ======================================================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Login with: admin@fraudshield.ai / admin123
echo.
echo Press any key to exit this window (services will continue running)
pause > nul
