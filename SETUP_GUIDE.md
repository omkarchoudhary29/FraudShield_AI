# FraudShield AI - Complete Setup Guide

This guide will walk you through setting up the entire FraudShield AI system from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **MongoDB 5.0+** - [Download](https://www.mongodb.com/try/download/community)
- **Git** (optional) - [Download](https://git-scm.com/)

## Step 1: MongoDB Setup

### Option A: Local MongoDB

1. Install MongoDB Community Edition
2. Start MongoDB service:
   ```bash
   # Windows
   net start MongoDB
   
   # macOS (with Homebrew)
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   ```

3. Verify MongoDB is running:
   ```bash
   mongosh
   # Should connect successfully
   ```

### Option B: MongoDB Atlas (Cloud)

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Get your connection string
4. Update `backend/.env` with your Atlas connection string

## Step 2: Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

5. Edit `.env` file with your settings:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=fraudshield_db
   JWT_SECRET=your-super-secret-key-change-this
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_MINUTES=1440
   MODEL_PATH=../ml/models/fraud_model.joblib
   SCALER_PATH=../ml/models/scaler.joblib
   ENCODER_PATH=../ml/models/encoder.joblib
   ```

## Step 3: Train the ML Model

1. Navigate to the ML directory:
   ```bash
   cd ../ml
   ```

2. Generate training dataset:
   ```bash
   python generate_dataset.py
   ```

3. Train the fraud detection model:
   ```bash
   python train_model.py
   ```

   This will:
   - Generate a synthetic fraud dataset
   - Train XGBoost and Random Forest models
   - Select the best performing model
   - Save the model, scaler, and encoder
   - Display performance metrics

   Expected output:
   ```
   Accuracy:  95%+
   Precision: 92%+
   Recall:    88%+
   F1 Score:  90%+
   AUC-ROC:   0.96+
   ```

## Step 4: Seed the Database

1. Navigate to the scripts directory:
   ```bash
   cd ../scripts
   ```

2. Run the seed script:
   ```bash
   python seed_data.py
   ```

   This will create:
   - 3 user accounts (admin, analyst, reviewer)
   - 50 user profiles
   - 200 sample transactions
   - Fraud predictions and alerts
   - Model version metadata

## Step 5: Start the Backend Server

1. Navigate back to the backend directory:
   ```bash
   cd ../backend
   ```

2. Ensure your virtual environment is activated

3. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Verify the server is running:
   - Open browser to http://localhost:8000
   - You should see: `{"message": "FraudShield AI API", "version": "1.0.0", "status": "operational"}`
   - API docs available at: http://localhost:8000/docs

## Step 6: Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

   This will install:
   - React 18
   - Vite
   - Tailwind CSS
   - Recharts
   - Lucide React icons
   - Axios

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser to http://localhost:5173

## Step 7: Login and Explore

Use these credentials to login:

| Role     | Email                      | Password    |
|----------|----------------------------|-------------|
| Admin    | admin@fraudshield.ai       | admin123    |
| Analyst  | analyst@fraudshield.ai     | analyst123  |
| Reviewer | reviewer@fraudshield.ai    | reviewer123 |

## Step 8: Start Transaction Simulator (Optional)

To see real-time fraud detection in action:

1. Open a new terminal
2. Navigate to scripts directory:
   ```bash
   cd scripts
   ```

3. Run the simulator:
   ```bash
   python simulate_transactions.py
   ```

   This will:
   - Generate transactions every 3-5 seconds
   - Mix normal and suspicious transactions
   - Display real-time fraud scores
   - Update the dashboard live

   To run a batch of transactions instead:
   ```bash
   python simulate_transactions.py batch 50
   ```

## Troubleshooting

### MongoDB Connection Issues

**Error:** `ServerSelectionTimeoutError`

**Solution:**
- Ensure MongoDB is running: `mongosh`
- Check connection string in `.env`
- For Atlas, ensure IP is whitelisted

### Python Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Model Not Found

**Error:** `Model not found. Please train the model first.`

**Solution:**
- Run the training script: `cd ml && python train_model.py`
- Verify files exist in `ml/models/` directory

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
- Backend: Change port in uvicorn command: `--port 8001`
- Frontend: Change port in `vite.config.js`

### CORS Issues

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Clear browser cache

## Project Structure

```
fraudshield-ai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # Main application
│   │   ├── models/      # Pydantic schemas
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   └── utils/       # Helper functions
│   └── package.json
├── ml/                  # Machine learning
│   ├── train_model.py   # Training pipeline
│   ├── generate_dataset.py
│   ├── models/          # Saved models
│   └── data/            # Training data
└── scripts/             # Utility scripts
    ├── seed_data.py     # Database seeding
    └── simulate_transactions.py
```

## Next Steps

1. **Explore the Dashboard** - View real-time metrics and fraud trends
2. **Monitor Transactions** - Filter and search through all transactions
3. **Review Suspicious Cases** - Use the analyst workflow to approve/block
4. **Analyze Patterns** - Explore fraud analytics and insights
5. **Check Model Performance** - View ML model metrics and feature importance

## Production Deployment

For production deployment:

1. **Backend:**
   - Use Gunicorn with Uvicorn workers
   - Set up proper environment variables
   - Use production MongoDB instance
   - Enable HTTPS

2. **Frontend:**
   - Build: `npm run build`
   - Serve with Nginx or similar
   - Update API URL in environment

3. **Security:**
   - Change JWT secret
   - Enable rate limiting
   - Set up proper authentication
   - Use environment-specific configs

## Support

For issues or questions:
- Check the troubleshooting section
- Review API docs at http://localhost:8000/docs
- Check console logs for errors

## Demo Tips

For the best demo experience:

1. Start with the Dashboard to show overview
2. Run the transaction simulator in the background
3. Show a high-risk transaction in detail
4. Demonstrate the analyst review workflow
5. Display analytics and model insights
6. Highlight the explainable AI features

Enjoy using FraudShield AI! 🛡️
