# FraudShield AI - Quick Start (5 Minutes)

Get FraudShield AI running in 5 minutes!

## Prerequisites Check

```bash
# Check Python
python --version  # Should be 3.9+

# Check Node.js
node --version    # Should be 18+

# Check MongoDB
mongosh          # Should connect
```

## Quick Setup

### 1. Install Backend Dependencies (1 min)
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment (30 sec)
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and set:
```env
MONGODB_URI=mongodb://localhost:27017
JWT_SECRET=change-this-secret-key
```

### 3. Train Model & Seed Data (2 min)
```bash
cd ../ml
python train_model.py

cd ../scripts
python seed_data.py
```

### 4. Start Backend (30 sec)
```bash
cd ../backend
uvicorn app.main:app --reload
```

Keep this terminal open. Backend runs on http://localhost:8000

### 5. Install & Start Frontend (1 min)

Open a NEW terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

## Login & Explore

Open http://localhost:5173 and login with:

- **Email**: admin@fraudshield.ai
- **Password**: admin123

## Optional: Start Transaction Simulator

Open a NEW terminal:

```bash
cd scripts
python simulate_transactions.py
```

Watch transactions appear in real-time!

## What to Demo

1. **Dashboard** - Real-time metrics and trends
2. **Transactions** - Click "View" on any high-risk transaction
3. **Review Queue** - Review and take action on suspicious transactions
4. **Analytics** - Explore fraud patterns
5. **Model Insights** - View AI model performance

## Troubleshooting

**MongoDB not running?**
```bash
# Windows
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

**Port already in use?**
```bash
# Backend: Use different port
uvicorn app.main:app --reload --port 8001

# Frontend: Edit vite.config.js
```

**Module not found?**
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

## Next Steps

- Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- Check [FEATURES.md](FEATURES.md) for complete feature list
- Review [README.md](README.md) for project overview

Enjoy! 🛡️
