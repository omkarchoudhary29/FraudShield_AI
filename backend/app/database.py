from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_uri)
    print(f"Connected to MongoDB at {settings.mongodb_uri}")
    
    # Create indexes
    database = db.client[settings.database_name]
    
    await database.transactions.create_index([("transaction_id", ASCENDING)], unique=True)
    await database.transactions.create_index([("user_id", ASCENDING)])
    await database.transactions.create_index([("timestamp", DESCENDING)])
    await database.transactions.create_index([("risk_level", ASCENDING)])
    
    await database.fraud_predictions.create_index([("transaction_id", ASCENDING)])
    await database.fraud_predictions.create_index([("fraud_probability", DESCENDING)])
    
    await database.users.create_index([("email", ASCENDING)], unique=True)
    await database.alerts.create_index([("status", ASCENDING)])
    await database.analyst_reviews.create_index([("transaction_id", ASCENDING)])
    
    print("Database indexes created")

async def close_mongo_connection():
    db.client.close()
    print("Closed MongoDB connection")

def get_database():
    return db.client[settings.database_name]
