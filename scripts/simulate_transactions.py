import asyncio
import aiohttp
import random
from datetime import datetime
import uuid

API_BASE_URL = "http://localhost:8001"
TOKEN = None

# Sample data
MERCHANTS = [
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
    ("Gift Card Store", "gift_cards"),
    ("Wire Transfer Service", "wire_transfer")
]

LOCATIONS = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"
]

USER_IDS = [f"user_{i:04d}" for i in range(1, 51)]

async def login():
    """Login and get JWT token"""
    global TOKEN
    
    async with aiohttp.ClientSession() as session:
        login_data = {
            "email": "admin@fraudshield.ai",
            "password": "admin123"
        }
        
        try:
            async with session.post(f"{API_BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    TOKEN = data["access_token"]
                    print("✓ Logged in successfully")
                    return True
                else:
                    print(f"✗ Login failed: {response.status}")
                    return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False

async def generate_transaction(suspicious=False):
    """Generate a random transaction"""
    user_id = random.choice(USER_IDS)
    merchant_name, merchant_category = random.choice(MERCHANTS)
    
    if suspicious:
        # Generate suspicious transaction
        amount = random.uniform(2000, 8000)
        # Prefer high-risk merchants
        high_risk = [m for m in MERCHANTS if m[1] in ["crypto", "gambling", "wire_transfer", "gift_cards"]]
        if high_risk:
            merchant_name, merchant_category = random.choice(high_risk)
    else:
        # Generate normal transaction
        amount = random.uniform(10, 500)
        # Prefer normal merchants
        normal = [m for m in MERCHANTS if m[1] not in ["crypto", "gambling", "wire_transfer"]]
        merchant_name, merchant_category = random.choice(normal)
    
    transaction = {
        "user_id": user_id,
        "amount": round(amount, 2),
        "merchant_name": merchant_name,
        "merchant_category": merchant_category,
        "location": random.choice(LOCATIONS),
        "device_id": f"device_{random.randint(1000, 9999)}",
        "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        "card_last_four": f"{random.randint(1000, 9999)}"
    }
    
    return transaction

async def submit_transaction(session, transaction):
    """Submit transaction to API"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        async with session.post(
            f"{API_BASE_URL}/transactions/ingest",
            json=transaction,
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                risk_level = data.get("risk_level", "Unknown")
                fraud_prob = data.get("fraud_probability", 0)
                
                # Color coding
                if risk_level == "Critical":
                    color = "\033[91m"  # Red
                elif risk_level == "High":
                    color = "\033[93m"  # Yellow
                elif risk_level == "Medium":
                    color = "\033[94m"  # Blue
                else:
                    color = "\033[92m"  # Green
                reset = "\033[0m"
                
                print(f"{color}[{risk_level}]{reset} ${transaction['amount']:.2f} at {transaction['merchant_name']} "
                      f"(Fraud: {fraud_prob:.2%}) - {data.get('status', 'unknown')}")
                return data
            else:
                print(f"✗ Transaction failed: {response.status}")
                return None
    except Exception as e:
        print(f"✗ Error submitting transaction: {e}")
        return None

async def simulate_continuous():
    """Continuously simulate transactions"""
    print("\n" + "="*70)
    print("FraudShield AI - Real-Time Transaction Simulator")
    print("="*70)
    print("\nSimulating transactions every 3-5 seconds...")
    print("Press Ctrl+C to stop\n")
    
    if not await login():
        print("Failed to login. Please ensure the backend is running.")
        return
    
    async with aiohttp.ClientSession() as session:
        transaction_count = 0
        fraud_detected = 0
        
        try:
            while True:
                # 15% chance of suspicious transaction
                is_suspicious = random.random() < 0.15
                
                transaction = await generate_transaction(suspicious=is_suspicious)
                result = await submit_transaction(session, transaction)
                
                if result:
                    transaction_count += 1
                    if result.get("risk_level") in ["High", "Critical"]:
                        fraud_detected += 1
                    
                    if transaction_count % 10 == 0:
                        fraud_rate = (fraud_detected / transaction_count * 100) if transaction_count > 0 else 0
                        print(f"\n--- Stats: {transaction_count} transactions, {fraud_detected} high-risk ({fraud_rate:.1f}%) ---\n")
                
                # Wait 3-5 seconds between transactions
                await asyncio.sleep(random.uniform(3, 5))
        
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("Simulation stopped")
            print("="*70)
            print(f"\nTotal transactions: {transaction_count}")
            print(f"High-risk detected: {fraud_detected}")
            if transaction_count > 0:
                print(f"Fraud rate: {fraud_detected / transaction_count * 100:.2f}%")

async def simulate_batch(count=20):
    """Simulate a batch of transactions"""
    print("\n" + "="*70)
    print(f"Simulating {count} transactions...")
    print("="*70 + "\n")
    
    if not await login():
        print("Failed to login. Please ensure the backend is running.")
        return
    
    async with aiohttp.ClientSession() as session:
        for i in range(count):
            is_suspicious = random.random() < 0.15
            transaction = await generate_transaction(suspicious=is_suspicious)
            await submit_transaction(session, transaction)
            await asyncio.sleep(0.5)
    
    print("\n✓ Batch simulation complete")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        asyncio.run(simulate_batch(count))
    else:
        asyncio.run(simulate_continuous())
