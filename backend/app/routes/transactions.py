from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import uuid
from app.models.schemas import (
    Transaction, TransactionCreate, User, TransactionStatus, RiskLevel
)
from app.utils.auth import get_current_user
from app.database import get_database
from app.services.fraud_detector import fraud_detector

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/ingest", response_model=Transaction)
async def ingest_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user)
):
    """Ingest a new transaction and run fraud detection"""
    db = get_database()
    
    # Create transaction
    transaction_id = str(uuid.uuid4())
    transaction = {
        "transaction_id": transaction_id,
        **transaction_data.dict(),
        "timestamp": datetime.utcnow(),
        "status": TransactionStatus.PENDING,
        "risk_level": None,
        "fraud_probability": None
    }
    
    # Run fraud detection
    prediction = await fraud_detector.predict(transaction)
    
    # Update transaction with prediction
    transaction["fraud_probability"] = prediction["fraud_probability"]
    transaction["risk_level"] = prediction["risk_level"]
    
    # Auto-block critical transactions
    if prediction["risk_level"] == RiskLevel.CRITICAL:
        transaction["status"] = TransactionStatus.BLOCKED
    elif prediction["risk_level"] in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
        transaction["status"] = TransactionStatus.UNDER_REVIEW
    else:
        transaction["status"] = TransactionStatus.APPROVED
    
    result = await db.transactions.insert_one(transaction)
    transaction["_id"] = str(result.inserted_id)
    
    # Store fraud prediction
    fraud_prediction = {
        "transaction_id": transaction_id,
        "fraud_probability": prediction["fraud_probability"],
        "is_fraud": prediction["is_fraud"],
        "risk_level": prediction["risk_level"],
        "model_version": prediction["model_version"],
        "prediction_timestamp": datetime.utcnow(),
        "explanation": prediction["explanation"],
        "top_reasons": prediction["top_reasons"]
    }
    await db.fraud_predictions.insert_one(fraud_prediction)
    
    # Create alert for high-risk transactions
    if prediction["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        alert = {
            "transaction_id": transaction_id,
            "alert_type": "high_risk_transaction",
            "severity": prediction["risk_level"],
            "message": f"High-risk transaction detected: {prediction['top_reasons'][0]}",
            "status": "open",
            "created_at": datetime.utcnow()
        }
        await db.alerts.insert_one(alert)
    
    # Update user profile
    await update_user_profile(db, transaction_data.user_id, transaction)
    
    return Transaction(**transaction)

@router.get("", response_model=List[Transaction])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    risk_level: Optional[RiskLevel] = None,
    status: Optional[TransactionStatus] = None,
    user_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get transactions with filtering"""
    db = get_database()
    
    query = {}
    if risk_level:
        query["risk_level"] = risk_level
    if status:
        query["status"] = status
    if user_id:
        query["user_id"] = user_id
    
    cursor = db.transactions.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    transactions = await cursor.to_list(length=limit)
    
    for txn in transactions:
        txn["_id"] = str(txn["_id"])
    
    return [Transaction(**txn) for txn in transactions]

@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific transaction"""
    db = get_database()
    transaction = await db.transactions.find_one({"transaction_id": transaction_id})
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction["_id"] = str(transaction["_id"])
    return Transaction(**transaction)

async def update_user_profile(db, user_id: str, transaction: dict):
    """Update user behavioral profile"""
    profile = await db.user_profiles.find_one({"user_id": user_id})
    
    if profile:
        # Update averages and lists
        total_txn = profile.get("total_transactions", 0)
        avg_amount = profile.get("avg_transaction_amount", 0)
        
        new_avg = (avg_amount * total_txn + transaction["amount"]) / (total_txn + 1)
        
        typical_merchants = profile.get("typical_merchants", [])
        if transaction["merchant_category"] not in typical_merchants:
            typical_merchants.append(transaction["merchant_category"])
        
        typical_locations = profile.get("typical_locations", [])
        if transaction["location"] not in typical_locations:
            typical_locations.append(transaction["location"])
        
        typical_devices = profile.get("typical_devices", [])
        if transaction["device_id"] not in typical_devices:
            typical_devices.append(transaction["device_id"])
        
        await db.user_profiles.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "avg_transaction_amount": new_avg,
                    "typical_merchants": typical_merchants[-10:],  # Keep last 10
                    "typical_locations": typical_locations[-5:],
                    "typical_devices": typical_devices[-3:],
                    "total_transactions": total_txn + 1,
                    "last_updated": datetime.utcnow()
                }
            }
        )
