import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "fraudshield_db"

async def seed_database():
    """Seed database with initial data"""
    
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    
    print("="*50)
    print("Seeding FraudShield AI Database")
    print("="*50)
    
    # Clear existing data
    print("\nClearing existing data...")
    await db.users.delete_many({})
    await db.transactions.delete_many({})
    await db.fraud_predictions.delete_many({})
    await db.alerts.delete_many({})
    await db.analyst_reviews.delete_many({})
    await db.user_profiles.delete_many({})
    await db.model_versions.delete_many({})
    await db.audit_logs.delete_many({})
    
    # Create users
    print("\nCreating users...")
    users = [
        {
            "email": "admin@fraudshield.ai",
            "full_name": "Admin User",
            "role": "admin",
            "hashed_password": pwd_context.hash("admin123"),
            "created_at": datetime.utcnow()
        },
        {
            "email": "analyst@fraudshield.ai",
            "full_name": "Fraud Analyst",
            "role": "analyst",
            "hashed_password": pwd_context.hash("analyst123"),
            "created_at": datetime.utcnow()
        },
        {
            "email": "reviewer@fraudshield.ai",
            "full_name": "Transaction Reviewer",
            "role": "reviewer",
            "hashed_password": pwd_context.hash("reviewer123"),
            "created_at": datetime.utcnow()
        }
    ]
    await db.users.insert_many(users)
    print(f"✓ Created {len(users)} users")
    
    # Create model version
    print("\nCreating model version...")
    model_version = {
        "version": "1.0.0",
        "model_type": "XGBoost",
        "accuracy": 0.95,
        "precision": 0.92,
        "recall": 0.88,
        "f1_score": 0.90,
        "auc_roc": 0.96,
        "threshold": 0.5,
        "is_active": True,
        "trained_at": datetime.utcnow(),
        "feature_importance": {
            "amount": 0.18,
            "amount_deviation": 0.15,
            "is_new_device": 0.12,
            "txn_last_hour": 0.11,
            "is_new_location": 0.10,
            "account_age_days": 0.08,
            "is_high_risk_merchant": 0.07,
            "high_velocity": 0.06,
            "is_new_account": 0.05,
            "fraud_history": 0.04
        }
    }
    await db.model_versions.insert_one(model_version)
    print("✓ Created model version")
    
    # Create sample user profiles
    print("\nCreating user profiles...")
    user_ids = [f"user_{i:04d}" for i in range(1, 51)]
    
    profiles = []
    for user_id in user_ids:
        profile = {
            "user_id": user_id,
            "avg_transaction_amount": random.uniform(50, 500),
            "typical_merchants": random.sample([
                "retail", "grocery", "restaurant", "gas_station", "online_shopping"
            ], k=3),
            "typical_locations": random.sample([
                "New York", "Los Angeles", "Chicago", "Houston", "Phoenix"
            ], k=2),
            "typical_devices": [f"device_{random.randint(1000, 9999)}"],
            "account_age_days": random.randint(30, 1000),
            "total_transactions": random.randint(10, 500),
            "fraud_history_count": 0,
            "last_updated": datetime.utcnow()
        }
        profiles.append(profile)
    
    await db.user_profiles.insert_many(profiles)
    print(f"✓ Created {len(profiles)} user profiles")
    
    # Create sample transactions
    print("\nCreating sample transactions...")
    
    merchants = [
        ("Amazon", "online_shopping"),
        ("Walmart", "retail"),
        ("Starbucks", "restaurant"),
        ("Shell Gas", "gas_station"),
        ("Whole Foods", "grocery"),
        ("Netflix", "entertainment"),
        ("Uber", "transportation"),
        ("Delta Airlines", "travel"),
        ("CVS Pharmacy", "healthcare"),
        ("Best Buy", "electronics"),
        ("Crypto Exchange", "crypto"),
        ("Online Casino", "gambling"),
        ("Gift Card Store", "gift_cards")
    ]
    
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                 "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    
    risk_levels = ["Low", "Medium", "High", "Critical"]
    statuses = ["approved", "pending", "under_review", "blocked"]
    
    transactions = []
    fraud_predictions = []
    alerts = []
    
    for i in range(200):
        user_id = random.choice(user_ids)
        merchant_name, merchant_category = random.choice(merchants)
        
        # Determine if this should be a suspicious transaction
        is_suspicious = random.random() < 0.15
        
        if is_suspicious:
            amount = random.uniform(1000, 5000)
            risk_level = random.choice(["High", "Critical"])
            fraud_prob = random.uniform(0.6, 0.95)
            status = random.choice(["under_review", "blocked"])
        else:
            amount = random.uniform(10, 500)
            risk_level = random.choice(["Low", "Medium"])
            fraud_prob = random.uniform(0.05, 0.45)
            status = "approved"
        
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        transaction = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": round(amount, 2),
            "merchant_name": merchant_name,
            "merchant_category": merchant_category,
            "location": random.choice(locations),
            "device_id": f"device_{random.randint(1000, 9999)}",
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "card_last_four": f"{random.randint(1000, 9999)}",
            "timestamp": timestamp,
            "status": status,
            "risk_level": risk_level,
            "fraud_probability": round(fraud_prob, 4)
        }
        transactions.append(transaction)
        
        # Create fraud prediction
        reasons = []
        if is_suspicious:
            reasons = random.sample([
                "Unusually high transaction amount",
                "Transaction from a new device",
                "Transaction from a new location",
                "High transaction velocity detected",
                "High-risk merchant category",
                "Suspicious round amount for high-value transaction"
            ], k=3)
        else:
            reasons = ["Transaction appears normal"]
        
        prediction = {
            "transaction_id": transaction_id,
            "fraud_probability": round(fraud_prob, 4),
            "is_fraud": fraud_prob >= 0.5,
            "risk_level": risk_level,
            "model_version": "1.0.0",
            "prediction_timestamp": timestamp,
            "explanation": {
                "fraud_probability": fraud_prob,
                "key_features": {
                    "amount": amount,
                    "amount_deviation": random.uniform(0, 3),
                    "new_device": is_suspicious,
                    "new_location": is_suspicious,
                    "transaction_velocity": random.randint(0, 5),
                    "account_age_days": random.randint(30, 1000)
                }
            },
            "top_reasons": reasons
        }
        fraud_predictions.append(prediction)
        
        # Create alert for high-risk transactions
        if risk_level in ["High", "Critical"]:
            alert = {
                "transaction_id": transaction_id,
                "alert_type": "high_risk_transaction",
                "severity": risk_level,
                "message": f"High-risk transaction detected: {reasons[0]}",
                "status": random.choice(["open", "acknowledged", "resolved"]),
                "created_at": timestamp
            }
            alerts.append(alert)
    
    await db.transactions.insert_many(transactions)
    print(f"✓ Created {len(transactions)} transactions")
    
    await db.fraud_predictions.insert_many(fraud_predictions)
    print(f"✓ Created {len(fraud_predictions)} fraud predictions")
    
    if alerts:
        await db.alerts.insert_many(alerts)
        print(f"✓ Created {len(alerts)} alerts")
    
    print("\n" + "="*50)
    print("Database seeding complete!")
    print("="*50)
    print("\nLogin credentials:")
    print("  Admin:    admin@fraudshield.ai / admin123")
    print("  Analyst:  analyst@fraudshield.ai / analyst123")
    print("  Reviewer: reviewer@fraudshield.ai / reviewer123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
