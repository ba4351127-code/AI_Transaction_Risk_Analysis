import pytest
from datetime import datetime, timedelta
from backend.app.engine.rules import evaluate_deterministic_rules
from backend.app.engine.behavioral import calculate_behavioral_deviation
from backend.app.engine.scorer import compute_composite_risk
from backend.app.utils.geo import haversine_distance_km, calculate_geo_velocity, normalize_to_utc
from datetime import timezone


def test_haversine_distance():
    # Mumbai to Delhi ~ 1,148 km
    dist = haversine_distance_km(19.0760, 72.8777, 28.7041, 77.1025)
    assert 1100.0 < dist < 1200.0


def test_geo_velocity_impossible_travel():
    # 1,148 km in 15 minutes = ~4,592 km/h
    t1 = datetime(2026, 11, 20, 10, 0, 0)
    t2 = datetime(2026, 11, 20, 10, 15, 0)
    dist, vel = calculate_geo_velocity(19.0760, 72.8777, t1, 28.7041, 77.1025, t2)
    assert vel > 4000.0

    rules = evaluate_deterministic_rules(
        amount=150.0,
        location_city="Delhi",
        is_device_familiar=True,
        curr_timestamp=t2,
        prev_location_city="Mumbai",
        prev_timestamp=t1
    )
    assert rules.hard_override_action == "BLOCK"
    assert "IMPOSSIBLE_TRAVEL_VELOCITY" in rules.rules_triggered


def test_normalize_to_utc_and_mixed_timezone_velocity():
    # 1. Test normalize_to_utc helper with diverse formats
    naive_dt = datetime(2026, 11, 22, 8, 30, 0)
    norm_naive = normalize_to_utc(naive_dt)
    assert norm_naive.tzinfo == timezone.utc
    assert norm_naive.hour == 8

    aware_dt = datetime(2026, 11, 22, 14, 0, 0, tzinfo=timezone.utc)
    norm_aware = normalize_to_utc(aware_dt)
    assert norm_aware.tzinfo == timezone.utc
    assert norm_aware.hour == 14

    iso_str_z = "2026-11-22T10:00:00Z"
    norm_iso = normalize_to_utc(iso_str_z)
    assert norm_iso.tzinfo == timezone.utc
    assert norm_iso.hour == 10

    assert normalize_to_utc(None) is None
    assert normalize_to_utc("invalid-date-string") is None

    # 2. Test calculate_geo_velocity with mixed naive and aware datetimes (reproduces previous bug)
    t_prev_naive = datetime(2026, 11, 22, 10, 0, 0)                  # naive (e.g. from SQLite)
    t_curr_aware = datetime(2026, 11, 22, 10, 30, 0, tzinfo=timezone.utc)  # aware (e.g. from request)
    dist_km, velocity_kmh = calculate_geo_velocity(
        19.0760, 72.8777, t_prev_naive,
        28.7041, 77.1025, t_curr_aware
    )
    assert dist_km > 1100.0
    assert velocity_kmh > 2000.0  # ~1148 km in 0.5h = ~2296 km/h

    # 3. Test with reverse order (aware prev, naive curr)
    dist_rev, vel_rev = calculate_geo_velocity(
        19.0760, 72.8777, t_curr_aware,
        28.7041, 77.1025, datetime(2026, 11, 22, 11, 0, 0)
    )
    assert dist_rev > 1100.0
    assert vel_rev > 2000.0


def test_composite_risk_normal_transaction():
    t = datetime(2026, 11, 20, 14, 0, 0)
    res = compute_composite_risk(
        amount=85.0,
        payment_method="credit_card",
        location_city="Mumbai",
        is_device_familiar=True,
        curr_timestamp=t,
        xgb_fraud_prob=0.01,
        iforest_outlier_score=5.0,
        raw_shap_list=[],
        transaction_ref="TEST-TX-001"
    )
    assert 0.0 <= res.overall_risk_score <= 30.0
    assert res.risk_category == "LOW"
    assert res.recommended_action == "APPROVE"
    assert res.everyday_user.badge_color == "#10B981"
    assert "Safe Transaction" in res.everyday_user.headline


def test_composite_risk_high_fraud():
    t = datetime(2026, 11, 20, 3, 30, 0)  # 3:30 AM
    res = compute_composite_risk(
        amount=7500.0,
        payment_method="credit_card",
        location_city="London",
        is_device_familiar=False,
        curr_timestamp=t,
        xgb_fraud_prob=0.88,
        iforest_outlier_score=85.0,
        raw_shap_list=[{"feature": "amount", "value": 7500.0, "shap_value": 0.42}],
        transaction_ref="TEST-TX-002"
    )
    assert res.overall_risk_score >= 70.0
    assert res.risk_category in ("HIGH", "CRITICAL")
    assert res.recommended_action == "BLOCK"
    assert len(res.everyday_user.simple_reasons) >= 1
    assert len(res.risk_analyst.top_shap_contributions) >= 1
