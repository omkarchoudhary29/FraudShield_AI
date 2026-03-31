# FraudShield AI - Automated Setup Script for Windows
# This script automates the entire setup process

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*69) -ForegroundColor Cyan
Write-Host "FraudShield AI - Automated Setup" -ForegroundColor Green
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

$allPrereqsMet = $true

# Check Python
if (Test-Command python) {
    $pythonVersion = python --version
    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[MISSING] Python 3.9+ is required" -ForegroundColor Red
    $allPrereqsMet = $false
}

# Check Node.js
if (Test-Command node) {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "[MISSING] Node.js 18+ is required" -ForegroundColor Red
    $allPrereqsMet = $false
}

# Check MongoDB
if (Test-Command mongosh) {
    Write-Host "[OK] MongoDB is installed" -ForegroundColor Green
} else {
    Write-Host "[WARNING] MongoDB not found. Please ensure MongoDB is running." -ForegroundColor Yellow
}

Write-Host ""

if (-not $allPrereqsMet) {
    Write-Host "Please install missing prerequisites and run this script again." -ForegroundColor Red
    exit 1
}

# Step 1: Backend Setup
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "Step 1: Setting up Backend" -ForegroundColor Green
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""

Set-Location backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "[OK] Python dependencies installed" -ForegroundColor Green

# Create .env file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "[OK] .env file created" -ForegroundColor Green
} else {
    Write-Host "[OK] .env file already exists" -ForegroundColor Green
}

Set-Location ..

# Step 2: Train ML Model
Write-Host ""
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "Step 2: Training ML Model" -ForegroundColor Green
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""

Set-Location ml

if (-not (Test-Path "models/fraud_model.joblib")) {
    Write-Host "Training fraud detection model..." -ForegroundColor Yellow
    python train_model.py
    Write-Host "[OK] Model trained successfully" -ForegroundColor Green
} else {
    Write-Host "[OK] Model already exists" -ForegroundColor Green
}

Set-Location ..

# Step 3: Seed Database
Write-Host ""
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "Step 3: Seeding Database" -ForegroundColor Green
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""

Set-Location scripts

Write-Host "Seeding database with initial data..." -ForegroundColor Yellow
python seed_data.py
Write-Host "[OK] Database seeded" -ForegroundColor Green

Set-Location ..

# Step 4: Frontend Setup
Write-Host ""
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "Step 4: Setting up Frontend" -ForegroundColor Green
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""

Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host "[OK] Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[OK] Node.js dependencies already installed" -ForegroundColor Green
}

Set-Location ..

# Setup Complete
Write-Host ""
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ("="*70) -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start Backend (in a new terminal):" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Start Frontend (in another new terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Cyan
Write-Host "   npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. (Optional) Start Transaction Simulator:" -ForegroundColor White
Write-Host "   cd scripts" -ForegroundColor Cyan
Write-Host "   python simulate_transactions.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor Yellow
Write-Host "  Admin:    admin@fraudshield.ai / admin123" -ForegroundColor White
Write-Host "  Analyst:  analyst@fraudshield.ai / analyst123" -ForegroundColor White
Write-Host "  Reviewer: reviewer@fraudshield.ai / reviewer123" -ForegroundColor White
Write-Host ""
Write-Host "Access the application at: http://localhost:5173" -ForegroundColor Green
Write-Host "API documentation at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
