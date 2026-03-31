from fastapi import APIRouter, Depends, Query
from typing import List
from datetime import datetime, timedelta
from app.models.schemas import User, OverviewMetrics, FraudTrend, MerchantRisk
from app.utils.auth import get_current_user
from app.database import get_database

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview", response_model=OverviewMetrics)
async def get_overview_metrics(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user)
):
    """Get overview metrics for dashboard"""
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total transactions
    total_transactions = await db.transactions.count_documents({
        "timestamp": {"$gte": start_date}
    })
    
    # Fraud detected
    fraud_detected = await db.transactions.count_documents({
        "timestamp": {"$gte": start_date},
        "risk_level": {"$in": ["High", "Critical"]}
    })
    
    # Blocked transactions
    blocked_transactions = await db.transactions.count_documents({
        "timestamp": {"$gte": start_date},
        "status": "blocked"
    })
    
    # Under review
    under_review = await db.transactions.count_documents({
        "timestamp": {"$gte": start_date},
        "status": "under_review"
    })
    
    # Calculate amounts
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {"$group": {
            "_id": None,
            "total_amount": {"$sum": "$amount"}
        }}
    ]
    result = await db.transactions.aggregate(pipeline).to_list(1)
    total_amount_processed = result[0]["total_amount"] if result else 0
    
    # Blocked amount
    pipeline_blocked = [
        {"$match": {
            "timestamp": {"$gte": start_date},
            "status": "blocked"
        }},
        {"$group": {
            "_id": None,
            "blocked_amount": {"$sum": "$amount"}
        }}
    ]
    result_blocked = await db.transactions.aggregate(pipeline_blocked).to_list(1)
    total_amount_blocked = result_blocked[0]["blocked_amount"] if result_blocked else 0
    
    fraud_rate = (fraud_detected / total_transactions * 100) if total_transactions > 0 else 0
    
    return OverviewMetrics(
        total_transactions=total_transactions,
        fraud_detected=fraud_detected,
        fraud_rate=round(fraud_rate, 2),
        blocked_transactions=blocked_transactions,
        under_review=under_review,
        total_amount_processed=round(total_amount_processed, 2),
        total_amount_blocked=round(total_amount_blocked, 2)
    )

@router.get("/fraud-trends", response_model=List[FraudTrend])
async def get_fraud_trends(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_user)
):
    """Get fraud trends over time"""
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$timestamp"
                }
            },
            "total_transactions": {"$sum": 1},
            "fraud_count": {
                "$sum": {
                    "$cond": [
                        {"$in": ["$risk_level", ["High", "Critical"]]},
                        1,
                        0
                    ]
                }
            }
        }},
        {"$sort": {"_id": 1}}
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(days)
    
    trends = []
    for result in results:
        fraud_rate = (result["fraud_count"] / result["total_transactions"] * 100) if result["total_transactions"] > 0 else 0
        trends.append(FraudTrend(
            date=result["_id"],
            total_transactions=result["total_transactions"],
            fraud_count=result["fraud_count"],
            fraud_rate=round(fraud_rate, 2)
        ))
    
    return trends

@router.get("/top-merchants", response_model=List[MerchantRisk])
async def get_top_merchants(
    days: int = Query(30, ge=1, le=90),
    limit: int = Query(10, ge=5, le=50),
    current_user: User = Depends(get_current_user)
):
    """Get merchant risk analysis"""
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {"$group": {
            "_id": "$merchant_category",
            "transaction_count": {"$sum": 1},
            "fraud_count": {
                "$sum": {
                    "$cond": [
                        {"$in": ["$risk_level", ["High", "Critical"]]},
                        1,
                        0
                    ]
                }
            },
            "total_amount": {"$sum": "$amount"}
        }},
        {"$sort": {"transaction_count": -1}},
        {"$limit": limit}
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(limit)
    
    merchants = []
    for result in results:
        fraud_rate = (result["fraud_count"] / result["transaction_count"] * 100) if result["transaction_count"] > 0 else 0
        merchants.append(MerchantRisk(
            merchant_category=result["_id"],
            transaction_count=result["transaction_count"],
            fraud_count=result["fraud_count"],
            fraud_rate=round(fraud_rate, 2),
            total_amount=round(result["total_amount"], 2)
        ))
    
    return merchants

@router.get("/device-risk")
async def get_device_risk(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user)
):
    """Get device risk analysis"""
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {"$group": {
            "_id": "$device_id",
            "transaction_count": {"$sum": 1},
            "fraud_count": {
                "$sum": {
                    "$cond": [
                        {"$in": ["$risk_level", ["High", "Critical"]]},
                        1,
                        0
                    ]
                }
            }
        }},
        {"$sort": {"fraud_count": -1}},
        {"$limit": 20}
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(20)
    
    devices = []
    for result in results:
        risk_score = (result["fraud_count"] / result["transaction_count"]) if result["transaction_count"] > 0 else 0
        devices.append({
            "device_id": result["_id"],
            "transaction_count": result["transaction_count"],
            "fraud_count": result["fraud_count"],
            "risk_score": round(risk_score, 2)
        })
    
    return devices

@router.get("/hourly-patterns")
async def get_hourly_patterns(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user)
):
    """Get fraud patterns by hour of day"""
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {"$group": {
            "_id": {"$hour": "$timestamp"},
            "total_transactions": {"$sum": 1},
            "fraud_count": {
                "$sum": {
                    "$cond": [
                        {"$in": ["$risk_level", ["High", "Critical"]]},
                        1,
                        0
                    ]
                }
            }
        }},
        {"$sort": {"_id": 1}}
    ]
    
    results = await db.transactions.aggregate(pipeline).to_list(24)
    
    patterns = []
    for result in results:
        fraud_rate = (result["fraud_count"] / result["total_transactions"] * 100) if result["total_transactions"] > 0 else 0
        patterns.append({
            "hour": result["_id"],
            "total_transactions": result["total_transactions"],
            "fraud_count": result["fraud_count"],
            "fraud_rate": round(fraud_rate, 2)
        })
    
    return patterns
