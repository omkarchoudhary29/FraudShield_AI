from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "fraudshield_db"
    jwt_secret: str = "your-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440
    model_path: str = "../ml/models/fraud_model.joblib"
    scaler_path: str = "../ml/models/scaler.joblib"
    encoder_path: str = "../ml/models/encoder.joblib"
    
    class Config:
        env_file = ".env"

settings = Settings()
