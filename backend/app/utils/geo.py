import math
from typing import Tuple, Optional, Any
from datetime import datetime, timezone

# Global registry of common financial transaction hubs with exact lat/long
CITY_COORDINATES = {
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.7041, 77.1025),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "pune": (18.5204, 73.8567),
    "new york": (40.7128, -74.0060),
    "london": (51.5074, -0.1278),
    "singapore": (1.3521, 103.8198),
    "tokyo": (35.6762, 139.6503),
    "dubai": (25.2048, 55.2708),
    "san francisco": (37.7749, -122.4194),
    "sydney": (-33.8688, 151.2093),
    "frankfurt": (50.1109, 8.6821),
    "toronto": (43.6532, -79.3832)
}


def normalize_to_utc(dt: Any) -> Optional[datetime]:
    """
    Normalizes any datetime (naive, aware, or ISO string) to a UTC-aware datetime.
    Returns None if dt is None or invalid.
    """
    if dt is None:
        return None
    if isinstance(dt, str):
        try:
            dt_str = dt.replace("Z", "+00:00")
            dt = datetime.fromisoformat(dt_str)
        except Exception:
            return None
    if not isinstance(dt, datetime):
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def resolve_city_coordinates(city_name: Optional[str]) -> Tuple[float, float]:
    """Resolves coordinates from city name, defaulting to Mumbai if unknown."""
    if not city_name:
        return (19.0760, 72.8777)
    normalized = city_name.strip().lower()
    return CITY_COORDINATES.get(normalized, (19.0760, 72.8777))


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two points on the Earth's surface
    using the Haversine formula in kilometers.
    """
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    r = 6371.0  # Earth's mean radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(r * c, 2)


def calculate_geo_velocity(
    prev_lat: float,
    prev_lon: float,
    prev_time: datetime,
    curr_lat: float,
    curr_lon: float,
    curr_time: datetime
) -> Tuple[float, float]:
    """
    Calculates distance (km) and speed (km/h) between two consecutive transactions.
    Normalizes timestamps to UTC to avoid naive vs aware datetime mismatch.
    Returns (distance_km, velocity_kmh).
    """
    dist_km = haversine_distance_km(prev_lat, prev_lon, curr_lat, curr_lon)

    t_prev = normalize_to_utc(prev_time)
    t_curr = normalize_to_utc(curr_time)

    if t_prev is None or t_curr is None:
        return round(dist_km, 2), 0.0

    time_delta_seconds = abs((t_curr - t_prev).total_seconds())

    if time_delta_seconds < 1.0:
        # Transactions under 1 second apart with spatial gap imply impossible speed
        velocity_kmh = dist_km * 3600.0 if dist_km > 1.0 else 0.0
    else:
        hours = time_delta_seconds / 3600.0
        velocity_kmh = dist_km / hours

    return round(dist_km, 2), round(velocity_kmh, 2)
