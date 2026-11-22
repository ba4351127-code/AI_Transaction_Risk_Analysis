from typing import Dict, Any, List, Optional
from datetime import datetime


def calculate_behavioral_deviation(
    amount: float,
    location_city: str,
    is_device_familiar: bool,
    timestamp: datetime,
    baseline: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates how much the current transaction deviates from the user's
    personal historical profile (30-day rolling baseline).
    Returns a normalized behavioral risk score (0 - 100) and deviation metrics.
    """
    if not baseline:
        # Cold start fallback: moderate default baseline
        baseline = {
            "avg_amount_30d": 350.0,
            "std_amount_30d": 150.0,
            "common_locations": ["mumbai", "delhi"],
            "usual_hours": list(range(8, 23))  # 8 AM to 11 PM
        }

    avg_amt = float(baseline.get("avg_amount_30d", 350.0))
    std_amt = float(baseline.get("std_amount_30d", 150.0))
    common_locs = [loc.lower() for loc in baseline.get("common_locations", [])]
    usual_hours = baseline.get("usual_hours", list(range(8, 23)))

    # Prevent division by zero
    safe_std = max(std_amt, 25.0)
    z_score = (amount - avg_amt) / safe_std

    score = 0.0
    insights: List[str] = []

    # 1. Amount Z-Score Evaluation
    if z_score > 3.0:
        score += min(50.0, z_score * 12.0)
        insights.append(f"Amount is {z_score:.1f} standard deviations above historical mean.")
    elif z_score > 1.5:
        score += z_score * 8.0
        insights.append(f"Amount moderately exceeds normal spending distribution (Z={z_score:.1f}).")
    elif z_score < -1.0:
        # Unusually low amounts typically don't increase risk
        pass

    # 2. Device Familiarity
    if not is_device_familiar:
        score += 25.0
        insights.append("Device fingerprint has not been seen in the last 30 days.")

    # 3. Location Deviation
    normalized_city = location_city.strip().lower()
    if common_locs and normalized_city not in common_locs:
        score += 20.0
        insights.append(f"Location '{location_city}' is outside the user's primary operating cities.")

    # 4. Temporal Hour Deviation
    hour = timestamp.hour
    if usual_hours and hour not in usual_hours:
        score += 15.0
        insights.append(f"Transaction time ({hour:02d}:00) occurs outside user's normal active hours.")

    # Bound behavioral score to [0, 100]
    behavioral_score = min(100.0, max(0.0, round(score, 2)))

    return {
        "behavioral_score": behavioral_score,
        "z_score": round(z_score, 2),
        "amount_ratio_to_mean": round(amount / max(avg_amt, 1.0), 2),
        "insights": insights
    }
