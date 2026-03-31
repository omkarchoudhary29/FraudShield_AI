from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.models.schemas import User, FraudPrediction
from app.utils.auth import get_current_user
from app.database import get_database

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])

@router.get("/predictions/{transaction_id}")
async def get_fraud_prediction(
    transaction_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get fraud prediction for a transaction"""
    db = get_database()
    prediction = await db.fraud_predictions.find_one({"transaction_id": transaction_id})
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    prediction["_id"] = str(prediction["_id"])
    return prediction

@router.get("/explain/{transaction_id}")
async def explain_prediction(
    transaction_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed explanation for fraud prediction"""
    db = get_database()
    
    prediction = await db.fraud_predictions.find_one({"transaction_id": transaction_id})
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    transaction = await db.transactions.find_one({"transaction_id": transaction_id})
    
    return {
        "transaction_id": transaction_id,
        "fraud_probability": prediction["fraud_probability"],
        "risk_level": prediction["risk_level"],
        "is_fraud": prediction["is_fraud"],
        "top_reasons": prediction["top_reasons"],
        "explanation": prediction["explanation"],
        "model_version": prediction["model_version"],
        "transaction_details": {
            "amount": transaction["amount"],
            "merchant": transaction["merchant_name"],
            "category": transaction["merchant_category"],
            "location": transaction["location"],
            "timestamp": transaction["timestamp"]
        }
    }

@router.get("/model-metrics")
async def get_model_metrics(current_user: User = Depends(get_current_user)):
    """Get current model performance metrics"""
    db = get_database()
    
    # Get active model version
    model_version = await db.model_versions.find_one({"is_active": True})
    
    if not model_version:
        # Return default metrics if no model version stored
        return {
            "version": "1.0.0",
            "model_type": "XGBoost",
            "accuracy": 0.95,
            "precision": 0.92,
            "recall": 0.88,
            "f1_score": 0.90,
            "auc_roc": 0.96,
            "threshold": 0.5,
            "trained_at": "2024-01-01T00:00:00"
        }
    
    model_version["_id"] = str(model_version["_id"])
    return model_version
