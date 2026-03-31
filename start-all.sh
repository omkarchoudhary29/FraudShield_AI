#!/bin/bash
# FraudShield AI - Start All Services (Linux/macOS)

echo "======================================================================"
echo "FraudShield AI - Starting All Services"
echo "======================================================================"
echo ""

# Start Backend
echo "Starting Backend Server..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "======================================================================"
echo "All services started!"
echo "======================================================================"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Login with: admin@fraudshield.ai / admin123"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
