import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path

# Fix random seed for reproducible benchmark datasets
random.seed(42)
np.random.seed(42)

CITIES = [
    ("Mumbai", 19.0760, 72.8777),
    ("Delhi", 28.7041, 77.1025),
    ("Bangalore", 12.9716, 77.5946),
    ("New York", 40.7128, -74.0060),
    ("London", 51.5074, -0.1278),
    ("Singapore", 1.3521, 103.8198),
    ("Tokyo", 35.6762, 139.6503),
    ("Dubai", 25.2048, 55.2708),
]

PAYMENT_METHODS = ["credit_card", "debit_card", "upi", "net_banking", "wire_transfer"]
CARD_NETWORKS = ["Visa", "Mastercard", "Amex", "Rupay"]
CATEGORIES = ["grocery", "electronics", "travel", "luxury_goods", "dining", "entertainment"]


def generate_synthetic_transactions(num_records: int = 5000, fraud_ratio: float = 0.04) -> pd.DataFrame:
    """
    Generates realistic financial transaction streams with injected fraud archetypes:
    - Normal transactions matching user baselines
    - Extreme amount spikes (fraud)
    - Unfamiliar device switching (fraud)
    - High-velocity bursts (fraud)
    - Anomalous midnight hour activity (fraud)
    """
    records = []
    base_time = datetime.utcnow() - timedelta(days=60)
    
    # 50 simulated user accounts with unique baselines
    users = []
    for i in range(1, 51):
        user_id = f"usr_{1000 + i}"
        avg_amt = random.uniform(80.0, 600.0)
        primary_city = random.choice(CITIES)
        known_dev = f"dev_{user_id}_primary"
        users.append({
            "user_id": user_id,
            "avg_amt": avg_amt,
            "std_amt": avg_amt * random.uniform(0.2, 0.45),
            "primary_city": primary_city,
            "known_dev": known_dev
        })

    num_fraud = int(num_records * fraud_ratio)
    num_legit = num_records - num_fraud

    # 1. Generate Legitimate Transactions
    for _ in range(num_legit):
        u = random.choice(users)
        amt = max(5.0, np.random.normal(u["avg_amt"], u["std_amt"]))
        amt = round(amt, 2)
        
        # Legitimate transactions mostly occur during active hours
        hour = int(np.random.choice(range(24), p=[
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02,
            0.04, 0.06, 0.07, 0.08, 0.08, 0.08,
            0.08, 0.07, 0.06, 0.06, 0.06, 0.06,
            0.05, 0.04, 0.02, 0.01, 0.005, 0.005
        ]))
        
        tx_time = base_time + timedelta(
            days=random.randint(0, 59),
            hours=hour,
            minutes=random.randint(0, 59)
        )
        
        # 95% familiar device for legit
        is_familiar = 1 if random.random() < 0.95 else 0
        city_name, lat, lon = u["primary_city"] if random.random() < 0.90 else random.choice(CITIES)

        records.append({
            "transaction_ref": f"TX-{random.randint(100000, 999999)}",
            "user_identifier": u["user_id"],
            "amount": amt,
            "amount_to_user_avg": round(amt / u["avg_amt"], 2),
            "payment_method": random.choice(PAYMENT_METHODS),
            "card_network": random.choice(CARD_NETWORKS),
            "merchant_category": random.choice(CATEGORIES),
            "location_city": city_name,
            "latitude": lat,
            "longitude": lon,
            "is_device_familiar": is_familiar,
            "transaction_hour": hour,
            "is_fraud": 0,
            "fraud_archetype": "legitimate",
            "timestamp": tx_time.isoformat()
        })

    # 2. Generate Fraudulent Transactions with explicit archetypes
    fraud_archetypes = [
        "amount_spike",
        "unfamiliar_device_takeover",
        "midnight_high_value",
        "velocity_burst"
    ]

    for _ in range(num_fraud):
        u = random.choice(users)
        archetype = random.choice(fraud_archetypes)
        
        if archetype == "amount_spike":
            # 8x to 25x normal baseline
            amt = round(u["avg_amt"] * random.uniform(8.0, 25.0), 2)
            is_familiar = 0
            hour = random.randint(0, 23)
            city_name, lat, lon = random.choice(CITIES)
            
        elif archetype == "unfamiliar_device_takeover":
            amt = round(u["avg_amt"] * random.uniform(3.0, 7.0), 2)
            is_familiar = 0
            hour = random.randint(1, 5)
            city_name, lat, lon = random.choice(CITIES)
            
        elif archetype == "midnight_high_value":
            amt = round(u["avg_amt"] * random.uniform(4.0, 10.0), 2)
            is_familiar = 0
            hour = random.randint(2, 4)
            city_name, lat, lon = random.choice(CITIES)
            
        else:  # velocity_burst
            amt = round(u["avg_amt"] * random.uniform(2.0, 5.0), 2)
            is_familiar = 0 if random.random() < 0.7 else 1
            hour = random.randint(10, 22)
            city_name, lat, lon = random.choice(CITIES)

        tx_time = base_time + timedelta(
            days=random.randint(0, 59),
            hours=hour,
            minutes=random.randint(0, 59)
        )

        records.append({
            "transaction_ref": f"TX-{random.randint(100000, 999999)}",
            "user_identifier": u["user_id"],
            "amount": amt,
            "amount_to_user_avg": round(amt / u["avg_amt"], 2),
            "payment_method": random.choice(PAYMENT_METHODS),
            "card_network": random.choice(CARD_NETWORKS),
            "merchant_category": random.choice(CATEGORIES),
            "location_city": city_name,
            "latitude": lat,
            "longitude": lon,
            "is_device_familiar": is_familiar,
            "transaction_hour": hour,
            "is_fraud": 1,
            "fraud_archetype": archetype,
            "timestamp": tx_time.isoformat()
        })

    # Shuffle records
    random.shuffle(records)
    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "data" / "synthetic"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "synthetic_transactions.csv"
    
    df = generate_synthetic_transactions(num_records=5000, fraud_ratio=0.04)
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} transactions -> {out_path}")
    print(f"Fraud distribution:\n{df['is_fraud'].value_counts(normalize=True)}")
