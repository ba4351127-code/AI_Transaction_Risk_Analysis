from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.utils.geo import calculate_geo_velocity, resolve_city_coordinates, normalize_to_utc
from backend.app.config import settings

# Example known blacklisted IPs or high-risk proxy ranges
KNOWN_SUSPICIOUS_IPS = {
    "198.51.100.24",
    "203.0.113.88",
    "185.220.101.5",  # Known Tor exit nodes / malicious proxies
    "185.220.101.6",
}


class RuleEvaluationResult:
    def __init__(self):
        self.penalty_score: float = 0.0
        self.rules_triggered: List[str] = []
        self.hard_override_action: Optional[str] = None  # "BLOCK" or None
        self.override_score: Optional[float] = None
        self.details: Dict[str, Any] = {}

    def add_violation(self, rule_name: str, penalty: float, detail: str):
        self.rules_triggered.append(rule_name)
        self.penalty_score += penalty
        self.details[rule_name] = detail

    def trigger_hard_block(self, rule_name: str, score: float, detail: str):
        self.rules_triggered.append(rule_name)
        self.hard_override_action = "BLOCK"
        self.override_score = max(self.override_score or 0.0, score)
        self.details[rule_name] = detail


def evaluate_deterministic_rules(
    amount: float,
    location_city: str,
    is_device_familiar: bool,
    curr_timestamp: datetime,
    ip_address: str = "127.0.0.1",
    user_avg_amount: float = 250.0,
    prev_location_city: Optional[str] = None,
    prev_timestamp: Optional[datetime] = None
) -> RuleEvaluationResult:
    """
    Evaluates hard heuristic financial rules against the current transaction.
    Returns RuleEvaluationResult containing penalty score and any hard overrides.
    """
    result = RuleEvaluationResult()
    curr_timestamp = normalize_to_utc(curr_timestamp) or datetime.now(timezone.utc)
    if prev_timestamp:
        prev_timestamp = normalize_to_utc(prev_timestamp)

    # 1. Blacklisted IP / Tor Proxy Check
    if ip_address in KNOWN_SUSPICIOUS_IPS:
        result.trigger_hard_block(
            "BLACKLISTED_IP_DETECTED",
            score=100.0,
            detail=f"Origin IP {ip_address} is listed on the global fraud/proxy blocklist."
        )

    # 2. Geo-Velocity / Impossible Travel Check
    if prev_location_city and prev_timestamp:
        lat1, lon1 = resolve_city_coordinates(prev_location_city)
        lat2, lon2 = resolve_city_coordinates(location_city)
        dist_km, velocity_kmh = calculate_geo_velocity(
            lat1, lon1, prev_timestamp,
            lat2, lon2, curr_timestamp
        )
        
        result.details["geo_velocity_kmh"] = velocity_kmh
        result.details["geo_distance_km"] = dist_km

        if velocity_kmh > settings.MAX_PLAUSIBLE_VELOCITY_KMH and dist_km > 300.0:
            result.trigger_hard_block(
                "IMPOSSIBLE_TRAVEL_VELOCITY",
                score=95.0,
                detail=f"Impossible physical velocity: {velocity_kmh} km/h between {prev_location_city} and {location_city} ({dist_km} km)."
            )
        elif velocity_kmh > 400.0 and dist_km > 100.0:
            result.add_violation(
                "SUSPICIOUS_TRAVEL_SPEED",
                penalty=25.0,
                detail=f"Rapid location change: {velocity_kmh} km/h ({dist_km} km) within short timeframe."
            )

    # 3. Sudden Extreme Amount Outlier
    if user_avg_amount > 0:
        amount_ratio = amount / user_avg_amount
        result.details["amount_to_avg_ratio"] = round(amount_ratio, 2)
        
        if amount_ratio >= 15.0 and amount > 2000.0:
            result.add_violation(
                "EXTREME_AMOUNT_SPIKE",
                penalty=40.0,
                detail=f"Transaction amount (${amount:,.2f}) is {amount_ratio:.1f}x higher than the typical baseline (${user_avg_amount:,.2f})."
            )
        elif amount_ratio >= 6.0 and amount > 1000.0:
            result.add_violation(
                "SIGNIFICANT_AMOUNT_OUTLIER",
                penalty=25.0,
                detail=f"Transaction amount is {amount_ratio:.1f}x typical spending average."
            )

    # 4. Unfamiliar Device Penalty
    if not is_device_familiar:
        penalty = 20.0
        # If unfamiliar device AND high amount, increase severity
        if amount > 1000.0:
            penalty = 30.0
        result.add_violation(
            "UNFAMILIAR_DEVICE_ACCESS",
            penalty=penalty,
            detail="Transaction originated from a new, previously unverified device."
        )

    # 5. High-Risk Time-of-Day Window (Midnight to 5 AM)
    hour = curr_timestamp.hour
    if 2 <= hour <= 5:
        if not is_device_familiar or amount > (user_avg_amount * 3.0):
            result.add_violation(
                "ANOMALOUS_HOUR_ACTIVITY",
                penalty=15.0,
                detail=f"High-value activity during dormant hours ({hour:02d}:00 UTC) from unverified context."
            )

    # Cap rule penalty to 100.0
    result.penalty_score = min(100.0, round(result.penalty_score, 2))
    return result
