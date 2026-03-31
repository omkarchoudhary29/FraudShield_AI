import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_fraud_dataset(n_samples=10000, fraud_ratio=0.15):
    """Generate synthetic fraud detection dataset"""
    
    np.random.seed(42)
    random.seed(42)
    
    n_fraud = int(n_samples * fraud_ratio)
    n_normal = n_samples - n_fraud
    
    # Merchant categories
    categories = [
        "retail", "grocery", "restaurant", "gas_station", "online_shopping",
        "entertainment", "travel", "healthcare", "utilities", "education",
        "gambling", "crypto", "wire_transfer", "gift_cards", "electronics"
    ]
    
    high_risk_categories = ["gambling", "crypto", "wire_transfer", "gift_cards", "electronics"]
    
    data = []
    
    # Generate normal transactions
    for i in range(n_normal):
        amount = np.random.lognormal(4, 1.2)  # Mean around $100
        amount = min(amount, 5000)  # Cap at $5000
        
        hour = np.random.choice(range(8, 22), p=[0.05, 0.08, 0.1, 0.12, 0.15, 0.15, 0.12, 0.1, 0.08, 0.03, 0.01, 0.01, 0, 0])
        is_night = 1 if (hour >= 22 or hour <= 6) else 0
        is_weekend = np.random.choice([0, 1], p=[0.7, 0.3])
        
        merchant_category = np.random.choice([c for c in categories if c not in high_risk_categories])
        is_high_risk_merchant = 0
        
        is_new_device = np.random.choice([0, 1], p=[0.9, 0.1])
        is_new_location = np.random.choice([0, 1], p=[0.85, 0.15])
        is_new_merchant = np.random.choice([0, 1], p=[0.7, 0.3])
        
        txn_last_hour = np.random.choice([0, 1, 2], p=[0.7, 0.25, 0.05])
        txn_last_day = np.random.poisson(3)
        high_velocity = 0
        
        account_age_days = np.random.randint(30, 1000)
        is_new_account = 0
        total_transactions = np.random.randint(10, 500)
        fraud_history = 0
        
        amount_deviation = np.random.uniform(0, 1)
        is_high_amount = 1 if amount > 1000 else 0
        is_round_amount = 1 if amount % 100 == 0 else 0
        
        data.append({
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
            "merchant_category": merchant_category,
            "is_fraud": 0
        })
    
    # Generate fraudulent transactions
    for i in range(n_fraud):
        # Fraudulent transactions have different patterns
        amount = np.random.lognormal(5.5, 1.5)  # Higher amounts
        amount = min(amount, 10000)
        
        # More transactions at night - normalized probabilities
        hour_weights = [0.08]*6 + [0.02]*10 + [0.08]*8
        hour_probs = np.array(hour_weights) / sum(hour_weights)
        hour = np.random.choice(range(24), p=hour_probs)
        is_night = 1 if (hour >= 22 or hour <= 6) else 0
        is_weekend = np.random.choice([0, 1], p=[0.5, 0.5])
        
        merchant_category = np.random.choice(categories, p=[0.03]*10 + [0.14]*5)  # Bias toward high-risk
        is_high_risk_merchant = 1 if merchant_category in high_risk_categories else 0
        
        is_new_device = np.random.choice([0, 1], p=[0.3, 0.7])  # More new devices
        is_new_location = np.random.choice([0, 1], p=[0.2, 0.8])  # More new locations
        is_new_merchant = np.random.choice([0, 1], p=[0.3, 0.7])
        
        txn_last_hour = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.2, 0.2, 0.2, 0.2, 0.1, 0.1])  # Higher velocity
        txn_last_day = np.random.poisson(8)
        high_velocity = 1 if txn_last_hour > 3 else 0
        
        account_age_days = np.random.choice([np.random.randint(0, 30), np.random.randint(30, 1000)], p=[0.4, 0.6])
        is_new_account = 1 if account_age_days < 30 else 0
        total_transactions = np.random.randint(0, 100)
        fraud_history = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
        
        amount_deviation = np.random.uniform(1.5, 5)  # Higher deviation
        is_high_amount = 1 if amount > 1000 else 0
        is_round_amount = np.random.choice([0, 1], p=[0.4, 0.6])  # More round amounts
        
        data.append({
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
            "merchant_category": merchant_category,
            "is_fraud": 1
        })
    
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle
    
    return df

if __name__ == "__main__":
    print("Generating fraud detection dataset...")
    df = generate_fraud_dataset(n_samples=10000, fraud_ratio=0.15)
    
    # Save dataset
    df.to_csv("data/fraud_dataset.csv", index=False)
    print(f"Dataset generated: {len(df)} samples")
    print(f"Fraud cases: {df['is_fraud'].sum()} ({df['is_fraud'].mean()*100:.2f}%)")
    print(f"Normal cases: {(~df['is_fraud'].astype(bool)).sum()}")
    print("\nDataset saved to data/fraud_dataset.csv")
