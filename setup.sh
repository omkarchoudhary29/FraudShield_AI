#!/bin/bash
# FraudShield AI - Automated Setup Script for Linux/macOS

echo "======================================================================"
echo "FraudShield AI - Automated Setup"
echo "======================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
echo ""

all_prereqs_met=true

# Check Python
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo -e "${GREEN}[OK] Python: $python_version${NC}"
else
    echo -e "${RED}[MISSING] Python 3.9+ is required${NC}"
    all_prereqs_met=false
fi

# Check Node.js
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo -e "${GREEN}[OK] Node.js: $node_version${NC}"
else
    echo -e "${RED}[MISSING] Node.js 18+ is required${NC}"
    all_prereqs_met=false
fi

# Check MongoDB
if command -v mongosh &> /dev/null; then
    echo -e "${GREEN}[OK] MongoDB is installed${NC}"
else
    echo -e "${YELLOW}[WARNING] MongoDB not found. Please ensure MongoDB is running.${NC}"
fi

echo ""

if [ "$all_prereqs_met" = false ]; then
    echo -e "${RED}Please install missing prerequisites and run this script again.${NC}"
    exit 1
fi

# Step 1: Backend Setup
echo "======================================================================"
echo -e "${GREEN}Step 1: Setting up Backend${NC}"
echo "======================================================================"
echo ""

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}[OK] Virtual environment created${NC}"
else
    echo -e "${GREEN}[OK] Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}[OK] Python dependencies installed${NC}"

# Create .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}[OK] .env file created${NC}"
else
    echo -e "${GREEN}[OK] .env file already exists${NC}"
fi

cd ..

# Step 2: Train ML Model
echo ""
echo "======================================================================"
echo -e "${GREEN}Step 2: Training ML Model${NC}"
echo "======================================================================"
echo ""

cd ml

if [ ! -f "models/fraud_model.joblib" ]; then
    echo -e "${YELLOW}Training fraud detection model...${NC}"
    python3 train_model.py
    echo -e "${GREEN}[OK] Model trained successfully${NC}"
else
    echo -e "${GREEN}[OK] Model already exists${NC}"
fi

cd ..

# Step 3: Seed Database
echo ""
echo "======================================================================"
echo -e "${GREEN}Step 3: Seeding Database${NC}"
echo "======================================================================"
echo ""

cd scripts

echo -e "${YELLOW}Seeding database with initial data...${NC}"
python3 seed_data.py
echo -e "${GREEN}[OK] Database seeded${NC}"

cd ..

# Step 4: Frontend Setup
echo ""
echo "======================================================================"
echo -e "${GREEN}Step 4: Setting up Frontend${NC}"
echo "======================================================================"
echo ""

cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
    echo -e "${GREEN}[OK] Node.js dependencies installed${NC}"
else
    echo -e "${GREEN}[OK] Node.js dependencies already installed${NC}"
fi

cd ..

# Setup Complete
echo ""
echo "======================================================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "======================================================================"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "${NC}1. Start Backend (in a new terminal):${NC}"
echo -e "${CYAN}   cd backend${NC}"
echo -e "${CYAN}   source venv/bin/activate${NC}"
echo -e "${CYAN}   uvicorn app.main:app --reload${NC}"
echo ""
echo -e "${NC}2. Start Frontend (in another new terminal):${NC}"
echo -e "${CYAN}   cd frontend${NC}"
echo -e "${CYAN}   npm run dev${NC}"
echo ""
echo -e "${NC}3. (Optional) Start Transaction Simulator:${NC}"
echo -e "${CYAN}   cd scripts${NC}"
echo -e "${CYAN}   python3 simulate_transactions.py${NC}"
echo ""
echo -e "${YELLOW}Login Credentials:${NC}"
echo -e "${NC}  Admin:    admin@fraudshield.ai / admin123${NC}"
echo -e "${NC}  Analyst:  analyst@fraudshield.ai / analyst123${NC}"
echo -e "${NC}  Reviewer: reviewer@fraudshield.ai / reviewer123${NC}"
echo ""
echo -e "${GREEN}Access the application at: http://localhost:5173${NC}"
echo -e "${GREEN}API documentation at: http://localhost:8000/docs${NC}"
echo ""
