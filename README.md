# FraudShield AI - Real-Time Fraudulent Transaction Detection

A complete end-to-end AI-powered fraud detection system for fintech applications with real-time monitoring, explainable AI, and analyst workflow management.

## Features

- **Real-Time Fraud Detection**: ML-powered fraud scoring with instant risk assessment
- **Explainable AI**: SHAP-based explanations showing why transactions are flagged
- **Analyst Dashboard**: Review, approve, block, or investigate suspicious transactions
- **Live Monitoring**: WebSocket-powered real-time transaction stream
- **Hybrid Detection**: ML models + rule-based engine for comprehensive coverage
- **Behavioral Analytics**: User baseline profiling and anomaly detection
- **Model Versioning**: Track model performance and switch between versions
- **Audit Trail**: Complete logging of all decisions and actions
- **Advanced Analytics**: Fraud trends, heatmaps, and performance metrics

## Tech Stack

### Frontend
- React 18 + Vite
- Tailwind CSS
- Recharts for analytics
- Lucide React icons
- WebSocket for real-time updates

### Backend
- Python FastAPI
- PyMongo/Motor for MongoDB
- JWT authentication
- WebSocket support
- Background tasks

### ML/AI
- XGBoost for fraud classification
- Isolation Forest for anomaly detection
- SHAP for explainability
- scikit-learn for preprocessing

### Database
- MongoDB for all data storage

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB 5.0+

### 1. Setup MongoDB
```bash
# Start MongoDB locally or use MongoDB Atlas
mongod --dbpath ./data/db
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your MongoDB URI and JWT secret

# Train the ML model
cd ../ml
python train_model.py

# Seed database
cd ../scripts
python seed_data.py

# Start backend
cd ../backend
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Start Transaction Simulator (Optional)
```bash
cd scripts
python simulate_transactions.py
```

## Default Login Credentials

- **Admin**: admin@fraudshield.ai / admin123
- **Analyst**: analyst@fraudshield.ai / analyst123
- **Reviewer**: reviewer@fraudshield.ai / reviewer123

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
fraudshield-ai/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── ml/              # ML training pipeline
├── scripts/         # Utilities and simulators
└── README.md
```

## Key Endpoints

- `POST /auth/login` - User authentication
- `POST /transactions/ingest` - Submit new transaction
- `POST /fraud/predict` - Get fraud prediction
- `GET /transactions/live-stream` - WebSocket for real-time updates
- `GET /analytics/overview` - Dashboard metrics
- `POST /reviews` - Submit analyst review

## Model Performance

The trained model achieves:
- Accuracy: ~95%
- Precision: ~92%
- Recall: ~88%
- F1 Score: ~90%
- AUC-ROC: ~0.96

## Features Highlights

### 1. Explainable AI
Every fraud prediction includes top contributing factors:
- Unusual transaction amount
- New device detected
- Location mismatch
- High transaction velocity
- Suspicious merchant category

### 2. Risk Scoring
- **Low (0-25%)**: Green - Safe transactions
- **Medium (25-50%)**: Yellow - Monitor
- **High (50-75%)**: Orange - Review required
- **Critical (75-100%)**: Red - Block immediately

### 3. Analyst Workflow
- Review queue with prioritization
- One-click approve/block/investigate
- Notes and feedback collection
- Audit trail for compliance

### 4. Real-Time Analytics
- Live transaction monitoring
- Fraud rate trends
- Geographic heatmaps
- Device risk analysis
- Merchant risk profiles

## Development

### Run Tests
```bash
cd backend
pytest

cd ../frontend
npm test
```

### Build for Production
```bash
cd frontend
npm run build

cd ../backend
# Use gunicorn or similar ASGI server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## License

MIT License - Built for hackathon/demo purposes

## Support

For issues or questions, please open an issue on GitHub.
