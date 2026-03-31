from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    BLOCKED = "blocked"
    UNDER_REVIEW = "under_review"

class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    REVIEWER = "reviewer"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    
    class Config:
        populate_by_name = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

# Transaction Models
class TransactionCreate(BaseModel):
    user_id: str
    amount: float
    merchant_name: str
    merchant_category: str
    location: str
    device_id: str
    ip_address: str
    card_last_four: str

class Transaction(BaseModel):
    id: str = Field(alias="_id")
    transaction_id: str
    user_id: str
    amount: float
    merchant_name: str
    merchant_category: str
    location: str
    device_id: str
    ip_address: str
    card_last_four: str
    timestamp: datetime
    status: TransactionStatus = TransactionStatus.PENDING
    risk_level: Optional[RiskLevel] = None
    fraud_probability: Optional[float] = None
    
    class Config:
        populate_by_name = True

# Fraud Prediction Models
class FraudPrediction(BaseModel):
    id: str = Field(alias="_id")
    transaction_id: str
    fraud_probability: float
    is_fraud: bool
    risk_level: RiskLevel
    model_version: str
    prediction_timestamp: datetime
    explanation: Dict[str, Any]
    top_reasons: List[str]
    
    class Config:
        populate_by_name = True

# Alert Models
class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class Alert(BaseModel):
    id: str = Field(alias="_id")
    transaction_id: str
    alert_type: str
    severity: RiskLevel
    message: str
    status: AlertStatus = AlertStatus.OPEN
    created_at: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

# Review Models
class ReviewDecision(str, Enum):
    APPROVE = "approve"
    BLOCK = "block"
    INVESTIGATE = "investigate"

class ReviewCreate(BaseModel):
    transaction_id: str
    decision: ReviewDecision
    notes: Optional[str] = None
    feedback_correct: Optional[bool] = None

class AnalystReview(BaseModel):
    id: str = Field(alias="_id")
    transaction_id: str
    analyst_id: str
    analyst_email: str
    decision: ReviewDecision
    notes: Optional[str] = None
    feedback_correct: Optional[bool] = None
    reviewed_at: datetime
    
    class Config:
        populate_by_name = True

# Model Version
class ModelVersion(BaseModel):
    id: str = Field(alias="_id")
    version: str
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    threshold: float
    is_active: bool
    trained_at: datetime
    feature_importance: Dict[str, float]
    
    class Config:
        populate_by_name = True

# Analytics Models
class OverviewMetrics(BaseModel):
    total_transactions: int
    fraud_detected: int
    fraud_rate: float
    blocked_transactions: int
    under_review: int
    total_amount_processed: float
    total_amount_blocked: float

class FraudTrend(BaseModel):
    date: str
    total_transactions: int
    fraud_count: int
    fraud_rate: float

class MerchantRisk(BaseModel):
    merchant_category: str
    transaction_count: int
    fraud_count: int
    fraud_rate: float
    total_amount: float

class DeviceRisk(BaseModel):
    device_id: str
    transaction_count: int
    fraud_count: int
    risk_score: float

# User Profile
class UserProfile(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    avg_transaction_amount: float
    typical_merchants: List[str]
    typical_locations: List[str]
    typical_devices: List[str]
    account_age_days: int
    total_transactions: int
    fraud_history_count: int
    last_updated: datetime
    
    class Config:
        populate_by_name = True

# Audit Log
class AuditLog(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: str
    
    class Config:
        populate_by_name = True
