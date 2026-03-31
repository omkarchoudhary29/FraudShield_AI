from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime
from app.models.schemas import User, Alert, AlertStatus
from app.utils.auth import get_current_user
from app.database import get_database

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[Alert])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: AlertStatus = None,
    current_user: User = Depends(get_current_user)
):
    """Get alerts"""
    db = get_database()
    
    query = {}
    if status:
        query["status"] = status
    
    cursor = db.alerts.find(query).sort("created_at", -1).skip(skip).limit(limit)
    alerts = await cursor.to_list(length=limit)
    
    for alert in alerts:
        alert["_id"] = str(alert["_id"])
    
    return [Alert(**alert) for alert in alerts]

@router.patch("/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status: AlertStatus,
    current_user: User = Depends(get_current_user)
):
    """Update alert status"""
    db = get_database()
    
    from bson import ObjectId
    try:
        obj_id = ObjectId(alert_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    
    update_data = {
        "status": status,
        "acknowledged_by": current_user.email,
        "acknowledged_at": datetime.utcnow()
    }
    
    result = await db.alerts.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert status updated", "status": status}
