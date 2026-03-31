from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime
from bson import ObjectId
from app.models.schemas import (
    User, ReviewCreate, AnalystReview, TransactionStatus
)
from app.utils.auth import get_current_user
from app.database import get_database

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("", response_model=AnalystReview)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user)
):
    """Create analyst review for a transaction"""
    db = get_database()
    
    # Check if transaction exists
    transaction = await db.transactions.find_one({"transaction_id": review_data.transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Create review
    review = {
        "transaction_id": review_data.transaction_id,
        "analyst_id": current_user.id,
        "analyst_email": current_user.email,
        "decision": review_data.decision,
        "notes": review_data.notes,
        "feedback_correct": review_data.feedback_correct,
        "reviewed_at": datetime.utcnow()
    }
    
    result = await db.analyst_reviews.insert_one(review)
    review["_id"] = str(result.inserted_id)
    
    # Update transaction status based on decision
    new_status = TransactionStatus.APPROVED
    if review_data.decision == "block":
        new_status = TransactionStatus.BLOCKED
    elif review_data.decision == "investigate":
        new_status = TransactionStatus.UNDER_REVIEW
    
    await db.transactions.update_one(
        {"transaction_id": review_data.transaction_id},
        {"$set": {"status": new_status}}
    )
    
    # Update alert status if exists
    await db.alerts.update_many(
        {"transaction_id": review_data.transaction_id, "status": "open"},
        {
            "$set": {
                "status": "resolved",
                "acknowledged_by": current_user.email,
                "acknowledged_at": datetime.utcnow()
            }
        }
    )
    
    # Log audit trail
    audit_log = {
        "user_id": current_user.id,
        "action": f"review_{review_data.decision}",
        "resource_type": "transaction",
        "resource_id": review_data.transaction_id,
        "details": {
            "decision": review_data.decision,
            "notes": review_data.notes,
            "feedback_correct": review_data.feedback_correct
        },
        "timestamp": datetime.utcnow(),
        "ip_address": "0.0.0.0"  # Should be extracted from request
    }
    await db.audit_logs.insert_one(audit_log)
    
    return AnalystReview(**review)

@router.get("", response_model=List[AnalystReview])
async def get_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    transaction_id: str = None,
    current_user: User = Depends(get_current_user)
):
    """Get analyst reviews"""
    db = get_database()
    
    query = {}
    if transaction_id:
        query["transaction_id"] = transaction_id
    
    cursor = db.analyst_reviews.find(query).sort("reviewed_at", -1).skip(skip).limit(limit)
    reviews = await cursor.to_list(length=limit)
    
    for review in reviews:
        review["_id"] = str(review["_id"])
    
    return [AnalystReview(**review) for review in reviews]

@router.get("/queue")
async def get_review_queue(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get transactions pending review"""
    db = get_database()
    
    # Get transactions under review or with high/critical risk
    query = {
        "$or": [
            {"status": "under_review"},
            {"risk_level": {"$in": ["High", "Critical"]}, "status": "pending"}
        ]
    }
    
    cursor = db.transactions.find(query).sort("timestamp", -1).limit(limit)
    transactions = await cursor.to_list(length=limit)
    
    # Get fraud predictions for each
    result = []
    for txn in transactions:
        txn["_id"] = str(txn["_id"])
        
        prediction = await db.fraud_predictions.find_one({"transaction_id": txn["transaction_id"]})
        if prediction:
            txn["fraud_details"] = {
                "top_reasons": prediction.get("top_reasons", []),
                "explanation": prediction.get("explanation", {})
            }
        
        result.append(txn)
    
    return result
