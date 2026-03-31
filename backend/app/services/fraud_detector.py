import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from app.config import settings
from app.database import get_database
from app.models.schemas import RiskLevel
import os

class FraudDetector:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.model_version = "1.0.0"
        self.threshold = 0.5
        self.load_model()
    
    def load_model(self):
        """Load trained model, scaler, and encoder"""
        try:
            if os.path.exists(settings.model_path):
                self.model = joblib.load(settings.model_path)
                self.scaler = joblib.load(settings.scaler_path)
                self.encoder = joblib.load(settings.encoder_path)
                print("Fraud detection model loaded successfully")
            else:
                print("Model not found. Please train the model first.")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get or create user behavioral profile"""
        db = get_database()
        profile = await db.user_profiles.find_one({"user_id": user_id})
        
        if not profile:
            # Create default profile for new user
            profile = {
                "user_id": user_id,
                "avg_transaction_amount": 100.0,
                "typical_merchants": [],
                "typical_locations": [],
                "typical_devices": [],
                "account_age_days": 0,
                "total_transactions": 0,
                "fraud_history_count": 0,
                "last_updated": datetime.utcnow()
            }
            await db.user_profiles.insert_one(profile)
        
        return profile
    
    async def calculate_velocity_features(self, user_id: str) -> Dict[str, float]:
        """Calculate transaction velocity features"""
        db = get_database()
        now = datetime.utcnow()
        
        # Transactions in last hour
        hour_ago = now - timedelta(hours=1)
        txn_last_hour = await db.transactions.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": hour_ago}
        })
        
        # Transactions in last 24 hours
        day_ago = now - timedelta(days=1)
        txn_last_day = await db.transactions.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": day_ago}
        })
        
        return {
            "txn_last_hour": txn_last_hour,
            "txn_last_day": txn_last_day
        }
    
    def engineer_features(self, transaction: Dict, user_profile: Dict, velocity: Dict) -> pd.DataFrame:
        """Engineer features for fraud detection"""
        
        # Time-based features
        hour = datetime.utcnow().hour
        is_night = 1 if (hour >= 22 or hour <= 6) else 0
        is_weekend = 1 if datetime.utcnow().weekday() >= 5 else 0
        
        # Amount-based features
        amount = transaction["amount"]
        avg_amount = user_profile.get("avg_transaction_amount", 100.0)
        amount_deviation = abs(amount - avg_amount) / (avg_amount + 1)
        is_high_amount = 1 if amount > 1000 else 0
        is_round_amount = 1 if amount % 100 == 0 else 0
        
        # Behavioral features
        device_id = transaction["device_id"]
        location = transaction["location"]
        merchant_category = transaction["merchant_category"]
        
        is_new_device = 0 if device_id in user_profile.get("typical_devices", []) else 1
        is_new_location = 0 if location in user_profile.get("typical_locations", []) else 1
        is_new_merchant = 0 if merchant_category in user_profile.get("typical_merchants", []) else 1
        
        # Velocity features
        txn_last_hour = velocity["txn_last_hour"]
        txn_last_day = velocity["txn_last_day"]
        high_velocity = 1 if txn_last_hour > 3 else 0
        
        # Account features
        account_age_days = user_profile.get("account_age_days", 0)
        is_new_account = 1 if account_age_days < 30 else 0
        total_transactions = user_profile.get("total_transactions", 0)
        fraud_history = user_profile.get("fraud_history_count", 0)
        
        # High-risk merchant categories
        high_risk_categories = ["gambling", "crypto", "wire_transfer", "gift_cards", "electronics"]
        is_high_risk_merchant = 1 if merchant_category.lower() in high_risk_categories else 0
        
        features = {
            "amount": amount,
            "hour": hour,
            "is_night": is_night,
            "is_weekend": is_weekend,
            "amount_deviation": amount_deviation,
            "is_high_amount": is_high_amount,
            "is_round_amount": is_round_amount,
            "is_new_device": is_new_device,
            "is_new_location": is_new_location,
            "is_new_merchant": is_new_merchant,
            "txn_last_hour": txn_last_hour,
            "txn_last_day": txn_last_day,
            "high_velocity": high_velocity,
            "account_age_days": account_age_days,
            "is_new_account": is_new_account,
            "total_transactions": total_transactions,
            "fraud_history": fraud_history,
            "is_high_risk_merchant": is_high_risk_merchant,
            "merchant_category": merchant_category
        }
        
        return pd.DataFrame([features])
    
    def get_risk_level(self, probability: float) -> RiskLevel:
        """Convert probability to risk level"""
        if probability < 0.25:
            return RiskLevel.LOW
        elif probability < 0.50:
            return RiskLevel.MEDIUM
        elif probability < 0.75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def generate_explanation(self, features: pd.DataFrame, probability: float) -> Tuple[Dict, List[str]]:
        """Generate human-readable explanation for the prediction"""
        reasons = []
        feature_dict = features.iloc[0].to_dict()
        
        # Analyze key risk factors
        if feature_dict.get("is_high_amount", 0) == 1:
            reasons.append("Unusually high transaction amount")
        
        if feature_dict.get("amount_deviation", 0) > 2:
            reasons.append("Amount significantly deviates from user's typical spending")
        
        if feature_dict.get("is_new_device", 0) == 1:
            reasons.append("Transaction from a new device")
        
        if feature_dict.get("is_new_location", 0) == 1:
            reasons.append("Transaction from a new location")
        
        if feature_dict.get("high_velocity", 0) == 1:
            reasons.append("High transaction velocity detected")
        
        if feature_dict.get("is_night", 0) == 1:
            reasons.append("Transaction during unusual hours (night time)")
        
        if feature_dict.get("is_new_account", 0) == 1:
            reasons.append("New account with limited history")
        
        if feature_dict.get("is_high_risk_merchant", 0) == 1:
            reasons.append("High-risk merchant category")
        
        if feature_dict.get("is_round_amount", 0) == 1 and feature_dict.get("is_high_amount", 0) == 1:
            reasons.append("Suspicious round amount for high-value transaction")
        
        if feature_dict.get("fraud_history", 0) > 0:
            reasons.append("User has previous fraud incidents")
        
        # If no specific reasons but high probability, add generic reason
        if not reasons and probability > 0.5:
            reasons.append("Multiple risk indicators detected")
        
        if not reasons:
            reasons.append("Transaction appears normal")
        
        explanation = {
            "fraud_probability": float(probability),
            "key_features": {
                "amount": float(feature_dict.get("amount", 0)),
                "amount_deviation": float(feature_dict.get("amount_deviation", 0)),
                "new_device": bool(feature_dict.get("is_new_device", 0)),
                "new_location": bool(feature_dict.get("is_new_location", 0)),
                "transaction_velocity": int(feature_dict.get("txn_last_hour", 0)),
                "account_age_days": int(feature_dict.get("account_age_days", 0))
            }
        }
        
        return explanation, reasons[:5]  # Return top 5 reasons
    
    async def predict(self, transaction: Dict) -> Dict[str, Any]:
        """Main prediction method"""
        if self.model is None:
            # Fallback to rule-based detection if model not loaded
            return await self.rule_based_detection(transaction)
        
        try:
            # Get user profile and velocity features
            user_profile = await self.get_user_profile(transaction["user_id"])
            velocity = await self.calculate_velocity_features(transaction["user_id"])
            
            # Engineer features
            features_df = self.engineer_features(transaction, user_profile, velocity)
            
            # Prepare features for model
            categorical_col = "merchant_category"
            if categorical_col in features_df.columns:
                cat_encoded = self.encoder.transform(features_df[[categorical_col]])
                features_df = features_df.drop(columns=[categorical_col])
                features_df = pd.concat([features_df, pd.DataFrame(cat_encoded, columns=self.encoder.get_feature_names_out())], axis=1)
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Predict
            fraud_probability = float(self.model.predict_proba(features_scaled)[0][1])
            is_fraud = fraud_probability >= self.threshold
            risk_level = self.get_risk_level(fraud_probability)
            
            # Generate explanation
            explanation, top_reasons = self.generate_explanation(features_df, fraud_probability)
            
            return {
                "fraud_probability": fraud_probability,
                "is_fraud": is_fraud,
                "risk_level": risk_level,
                "model_version": self.model_version,
                "explanation": explanation,
                "top_reasons": top_reasons
            }
        
        except Exception as e:
            print(f"Error in prediction: {e}")
            return await self.rule_based_detection(transaction)
    
    async def rule_based_detection(self, transaction: Dict) -> Dict[str, Any]:
        """Fallback rule-based fraud detection"""
        score = 0.0
        reasons = []
        
        # Rule 1: High amount
        if transaction["amount"] > 5000:
            score += 0.3
            reasons.append("Very high transaction amount")
        elif transaction["amount"] > 1000:
            score += 0.15
            reasons.append("High transaction amount")
        
        # Rule 2: High-risk merchant
        high_risk = ["gambling", "crypto", "wire_transfer"]
        if any(risk in transaction["merchant_category"].lower() for risk in high_risk):
            score += 0.25
            reasons.append("High-risk merchant category")
        
        # Rule 3: Round amounts (potential testing)
        if transaction["amount"] % 100 == 0 and transaction["amount"] > 500:
            score += 0.1
            reasons.append("Suspicious round amount")
        
        # Rule 4: Night time transaction
        hour = datetime.utcnow().hour
        if hour >= 22 or hour <= 6:
            score += 0.1
            reasons.append("Transaction during unusual hours")
        
        fraud_probability = min(score, 0.99)
        is_fraud = fraud_probability >= 0.5
        risk_level = self.get_risk_level(fraud_probability)
        
        if not reasons:
            reasons.append("Transaction appears normal")
        
        return {
            "fraud_probability": fraud_probability,
            "is_fraud": is_fraud,
            "risk_level": risk_level,
            "model_version": "rule-based",
            "explanation": {"fraud_probability": fraud_probability},
            "top_reasons": reasons
        }

# Global instance
fraud_detector = FraudDetector()
