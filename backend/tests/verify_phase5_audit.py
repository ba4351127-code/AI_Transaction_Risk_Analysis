import urllib.request
import json
import uuid
import sys
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DB_PATH = REPO_ROOT / "backend" / "transactionguard.db"
STATE_FILE = SCRIPT_DIR / "restart_state.json"

def api_call(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if "application/json" in content_type:
                return resp.status, json.loads(raw.decode("utf-8"))
            return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def run_phase5_master_audit():
    print("=" * 90)
    print("PHASE 5: FINAL END-TO-END SYSTEM AUDIT - TRANSACTIONGUARD AI")
    print(f"Target: {BASE_URL} | Database: {DB_PATH}")
    print("=" * 90)

    total_tests = 0
    passed_tests = 0

    def assert_test(condition, test_name, detail=""):
        nonlocal total_tests, passed_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"  [PASS] {test_name} {detail}")
        else:
            print(f"  [FAIL] {test_name} {detail}")
            raise AssertionError(f"Test failed: {test_name} - {detail}")

    # =========================================================================
    # 1. AUTHENTICATION & MULTI-USER ISOLATION AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("1. AUTHENTICATION & MULTI-USER ISOLATION AUDIT")
    print("=" * 50)

    email_user1 = f"audit_user1_{uuid.uuid4().hex[:6]}@transactionguard.ai"
    pwd_user1 = "SecurePass2026!"
    email_user2 = f"audit_user2_{uuid.uuid4().hex[:6]}@transactionguard.ai"
    pwd_user2 = "SecurePass2026!"

    # 1.1 User 1 Registration
    s, r = api_call("POST", "/api/v1/auth/signup", {"email": email_user1, "password": pwd_user1, "full_name": "Audit User One"})
    assert_test(s == 201 and "access_token" in r and "user" in r, "1.1 User 1 Registration", f"Status: {s}, ID: {r.get('user', {}).get('id')}")
    token_u1 = r["access_token"]
    id_u1 = r["user"]["id"]
    identifier_u1 = r["user"]["user_identifier"]

    # 1.2 User 2 Registration
    s, r = api_call("POST", "/api/v1/auth/signup", {"email": email_user2, "password": pwd_user2, "full_name": "Audit User Two"})
    assert_test(s == 201 and "access_token" in r, "1.2 User 2 Registration", f"Status: {s}, ID: {r.get('user', {}).get('id')}")
    token_u2 = r["access_token"]
    id_u2 = r["user"]["id"]
    identifier_u2 = r["user"]["user_identifier"]

    # 1.3 Duplicate Email Registration Rejection
    s, r = api_call("POST", "/api/v1/auth/signup", {"email": email_user1, "password": pwd_user1, "full_name": "Duplicate User"})
    assert_test(s == 400 and "already exists" in str(r).lower(), "1.3 Duplicate Email Rejection", f"Status: {s}")

    # 1.4 Valid Login
    s, r = api_call("POST", "/api/v1/auth/login", {"email": email_user1, "password": pwd_user1})
    assert_test(s == 200 and r.get("user", {}).get("email") == email_user1 and "access_token" in r, "1.4 Login Authentication", f"Status: {s}")
    token_u1 = r["access_token"]

    # 1.5 Invalid Password Rejection
    s, r = api_call("POST", "/api/v1/auth/login", {"email": email_user1, "password": "WrongPassword!"})
    assert_test(s == 401 and "invalid" in str(r).lower(), "1.5 Invalid Password Rejection", f"Status: {s}")

    # 1.6 Non-existent User Login Rejection
    s, r = api_call("POST", "/api/v1/auth/login", {"email": "ghost_user@transactionguard.ai", "password": pwd_user1})
    assert_test(s == 401 and "invalid" in str(r).lower(), "1.6 Non-Existent User Rejection", f"Status: {s}")

    # 1.7 Bcrypt 72-Byte Password Ceiling Validation
    s, r = api_call("POST", "/api/v1/auth/signup", {"email": f"long_{uuid.uuid4().hex[:6]}@tg.ai", "password": "X" * 80, "full_name": "Long Password"})
    assert_test(s == 422 and "72 bytes" in str(r).lower(), "1.7 Password > 72 Bytes Rejection", f"Status: {s}")

    # 1.8 Profile with JWT Bearer Token
    s, r = api_call("GET", "/api/v1/auth/me", token=token_u1)
    assert_test(s == 200 and r.get("email") == email_user1, "1.8 Profile GET /auth/me with Token", f"Email: {r.get('email')}")

    # 1.9 Unauthorized Profile Access (No Token)
    s, r = api_call("GET", "/api/v1/auth/me")
    assert_test(s == 401, "1.9 Unauthorized Profile Access Rejection", f"Status: {s}")

    # 1.10 Invalid Token Rejection
    s, r = api_call("GET", "/api/v1/auth/me", token="invalid_tampered_jwt_token_payload")
    assert_test(s == 401, "1.10 Invalid/Tampered JWT Token Rejection", f"Status: {s}")

    # =========================================================================
    # 2. TRANSACTION ANALYSIS & RISK ENGINE AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("2. TRANSACTION ANALYSIS & RISK ENGINE AUDIT")
    print("=" * 50)

    # 2.1 Low-Risk Transaction
    tx_low = {
        "amount": 35.00,
        "currency": "USD",
        "payment_method": "credit_card",
        "location_city": "Mumbai",
        "is_device_familiar": True
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_low, token=token_u1)
    assert_test(s == 200 and r["risk_category"] == "LOW" and r["recommended_action"] == "APPROVE" and r["overall_risk_score"] < 30.0,
                "2.1 Low-Risk Transaction Analysis", f"Score: {r['overall_risk_score']}, Category: {r['risk_category']}, Action: {r['recommended_action']}")
    u1_low_ref = r["transaction_ref"]

    # 2.2 Medium-Risk Transaction (higher amount, unfamiliar device, different city 6 hours later)
    t2_time = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
    tx_med = {
        "amount": 750.00,
        "currency": "EUR",
        "payment_method": "debit_card",
        "location_city": "Bangalore",
        "is_device_familiar": False,
        "transaction_timestamp": t2_time,
        "advanced_details": {"merchant_category": "electronics"}
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_med, token=token_u1)
    assert_test(s == 200 and r["risk_category"] == "MEDIUM" and r["recommended_action"] == "REVIEW",
                "2.2 Medium-Risk Transaction Analysis", f"Score: {r['overall_risk_score']}, Category: {r['risk_category']}, Action: {r['recommended_action']}")
    u1_med_ref = r["transaction_ref"]

    # 2.3 High-Risk Transaction (large luxury amount, unfamiliar device, offshore location)
    t3_time = (datetime.now(timezone.utc) + timedelta(hours=14)).isoformat()
    tx_high = {
        "amount": 9500.00,
        "currency": "GBP",
        "payment_method": "credit_card",
        "location_city": "Dubai",
        "is_device_familiar": False,
        "transaction_timestamp": t3_time,
        "advanced_details": {"merchant_category": "luxury"}
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_high, token=token_u1)
    assert_test(s == 200 and r["risk_category"] in ("HIGH", "CRITICAL") and r["recommended_action"] == "BLOCK",
                "2.3 High-Risk Transaction Analysis", f"Score: {r['overall_risk_score']}, Category: {r['risk_category']}, Action: {r['recommended_action']}")
    u1_high_ref = r["transaction_ref"]

    # 2.4 User 2: Safe Fast UPI Transaction
    tx_u2_safe = {
        "amount": 180.00,
        "currency": "INR",
        "payment_method": "upi",
        "location_city": "Delhi",
        "is_device_familiar": True
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_u2_safe, token=token_u2)
    assert_test(s == 200 and r["risk_category"] == "LOW" and r["recommended_action"] == "APPROVE",
                "2.4 User 2 Safe Domestic UPI", f"Score: {r['overall_risk_score']}, Category: {r['risk_category']}")
    u2_safe_ref = r["transaction_ref"]

    # 2.5 User 2: Geo-Velocity Impossible Travel Circuit Breaker (London -> Tokyo in 1 second)
    tx_u2_lon = {
        "amount": 120.00,
        "currency": "GBP",
        "payment_method": "credit_card",
        "location_city": "London",
        "is_device_familiar": True
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_u2_lon, token=token_u2)
    assert_test(s == 200, "2.5 User 2 Baseline Tx (London)", f"Ref: {r['transaction_ref']}")

    tx_u2_tokyo = {
        "amount": 7500.00,
        "currency": "USD",
        "payment_method": "credit_card",
        "location_city": "Tokyo",
        "is_device_familiar": False
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_u2_tokyo, token=token_u2)
    assert_test(s == 200 and r["overall_risk_score"] >= 95.0 and r["recommended_action"] == "BLOCK" and "IMPOSSIBLE_TRAVEL_VELOCITY" in r.get("risk_analyst", {}).get("rules_triggered", []),
                "2.6 Impossible Travel Velocity Circuit Breaker", f"Score: {r['overall_risk_score']}, Rules: {r.get('risk_analyst', {}).get('rules_triggered')}")
    u2_tokyo_ref = r["transaction_ref"]

    # 2.7 Unknown / Unmapped City Fallback ("Reykjavik")
    t_reyk = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 55.00, "location_city": "Reykjavik", "payment_method": "credit_card", "is_device_familiar": True, "transaction_timestamp": t_reyk}, token=token_u1)
    assert_test(s == 200 and "overall_risk_score" in r, "2.7 Unknown City Graceful Fallback", f"Score: {r['overall_risk_score']}")

    # 2.8 Input Validation: Negative Amount
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": -100.0, "location_city": "Mumbai"}, token=token_u1)
    assert_test(s == 422 and "greater than 0" in str(r).lower(), "2.8 Negative Amount Rejected with 422", f"Status: {s}")

    # 2.9 Input Validation: Zero Amount
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 0.0, "location_city": "Mumbai"}, token=token_u1)
    assert_test(s == 422 and "greater than 0" in str(r).lower(), "2.9 Zero Amount Rejected with 422", f"Status: {s}")

    # 2.10 Input Validation: Ceiling Breach (>$100M)
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 105_000_000.0, "location_city": "Mumbai"}, token=token_u1)
    assert_test(s == 422 and "ceiling" in str(r).lower(), "2.10 Amount > $100M Rejected with 422", f"Status: {s}")

    # 2.11 Input Validation: Unsupported Payment Method
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 50.0, "payment_method": "unsupported_pay", "location_city": "Mumbai"}, token=token_u1)
    assert_test(s == 422 and "supported payment methods" in str(r).lower(), "2.11 Unsupported Payment Method Rejected with 422", f"Status: {s}")

    # 2.12 Input Validation: Unsupported Currency
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 50.0, "currency": "BITCOIN", "location_city": "Mumbai"}, token=token_u1)
    assert_test(s == 422 and "supported currencies" in str(r).lower(), "2.12 Unsupported Currency Rejected with 422", f"Status: {s}")

    # 2.13 Input Validation: Empty / Whitespace City
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 50.0, "location_city": "   "}, token=token_u1)
    assert_test(s == 422 and "city cannot be empty" in str(r).lower(), "2.13 Empty City Rejected with 422", f"Status: {s}")

    # =========================================================================
    # 3. ML INTEGRATION & EXPLAINABILITY AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("3. ML INTEGRATION & EXPLAINABILITY AUDIT")
    print("=" * 50)

    # 3.1 Verify Real Supervised XGBoost Probability
    t_ml_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    s, r_ml = api_call("POST", "/api/v1/transactions/analyze", {
        "amount": 650.0,
        "payment_method": "credit_card",
        "location_city": "Mumbai",
        "is_device_familiar": True,
        "transaction_timestamp": t_ml_time
    }, token=token_u1)
    diag = r_ml.get("risk_analyst", {}).get("model_signals", {})
    shap_list = r_ml.get("risk_analyst", {}).get("top_shap_contributions", [])

    xgb_prob = diag.get("xgb_fraud_probability")
    assert_test(xgb_prob is not None and 0.0 <= xgb_prob <= 1.0,
                "3.1 Real Supervised XGBoost Fraud Probability", f"P(Fraud): {xgb_prob}")

    # 3.2 Verify Real Unsupervised Isolation Forest Anomaly Score
    iforest_score = diag.get("iforest_anomaly_score")
    assert_test(iforest_score is not None and 0.0 <= iforest_score <= 100.0,
                "3.2 Real Unsupervised Isolation Forest Anomaly Score", f"Anomaly Score: {iforest_score} / 100")

    # 3.3 Verify Top SHAP Feature Explanations
    assert_test(len(shap_list) >= 3 and all("shap_value" in f and "display_name" in f and "value" in f for f in shap_list),
                "3.3 Real SHAP Explainability Waterfall Features", f"SHAP count: {len(shap_list)}, Top: {shap_list[0]['display_name']} ({shap_list[0]['shap_value']:+.4f})")

    # 3.4 Dual Persona Explanations (Everyday User + Risk Analyst)
    everyday = r_ml.get("everyday_user", {})
    analyst = r_ml.get("risk_analyst", {})
    assert_test(bool(everyday.get("headline")) and len(everyday.get("simple_reasons", [])) >= 1 and bool(everyday.get("action_advice")) and bool(analyst.get("technical_summary")),
                "3.4 Dual Persona Plain English & Technical Explanations", f"Headline: '{everyday.get('headline')}', Advice: '{everyday.get('action_advice')}'")

    # =========================================================================
    # 4. USER DATA ISOLATION ENFORCEMENT AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("4. USER DATA ISOLATION ENFORCEMENT AUDIT")
    print("=" * 50)

    # 4.1 Transaction History Isolation
    s, h_u1 = api_call("GET", "/api/v1/transactions/history", token=token_u1)
    u1_refs = [x["transaction_ref"] for x in h_u1["records"]]
    s, h_u2 = api_call("GET", "/api/v1/transactions/history", token=token_u2)
    u2_refs = [x["transaction_ref"] for x in h_u2["records"]]

    assert_test(u1_high_ref in u1_refs and u1_high_ref not in u2_refs,
                "4.1 User 1 Transactions Inaccessible to User 2", f"User 1 count: {len(u1_refs)}")
    assert_test(u2_tokyo_ref in u2_refs and u2_tokyo_ref not in u1_refs,
                "4.2 User 2 Transactions Inaccessible to User 1", f"User 2 count: {len(u2_refs)}")

    # 4.2 Security Alerts Feed Isolation
    s, a_u1 = api_call("GET", "/api/v1/alerts/feed", token=token_u1)
    u1_alert_refs = [a["transaction_ref"] for a in a_u1]
    s, a_u2 = api_call("GET", "/api/v1/alerts/feed", token=token_u2)
    u2_alert_refs = [a["transaction_ref"] for a in a_u2]

    assert_test(u1_high_ref in u1_alert_refs and u1_high_ref not in u2_alert_refs,
                "4.3 User 1 Security Alerts Isolated from User 2", f"User 1 Alerts: {len(u1_alert_refs)}")
    assert_test(u2_tokyo_ref in u2_alert_refs and u2_tokyo_ref not in u1_alert_refs,
                "4.4 User 2 Security Alerts Isolated from User 1", f"User 2 Alerts: {len(u2_alert_refs)}")

    # 4.3 CSV Report Scoped Strictly to Authenticated User
    s, csv_u1 = api_call("GET", "/api/v1/reports/export/csv", token=token_u1)
    csv_u1_text = csv_u1.decode("utf-8") if isinstance(csv_u1, bytes) else str(csv_u1)
    s, csv_u2 = api_call("GET", "/api/v1/reports/export/csv", token=token_u2)
    csv_u2_text = csv_u2.decode("utf-8") if isinstance(csv_u2, bytes) else str(csv_u2)

    assert_test(u1_high_ref in csv_u1_text and u2_tokyo_ref not in csv_u1_text,
                "4.5 User 1 CSV Contains Zero User 2 Transactions", "Strictly scoped")
    assert_test(u2_tokyo_ref in csv_u2_text and u1_high_ref not in csv_u2_text,
                "4.6 User 2 CSV Contains Zero User 1 Transactions", "Strictly scoped")

    # 4.4 Direct Single-Tx PDF Export Isolation (Attempt to export User 2's Tx with User 1's Token)
    s, r = api_call("GET", f"/api/v1/reports/export/pdf/{u2_tokyo_ref}", token=token_u1)
    assert_test(s == 404, "4.7 Direct Unauthorized PDF Export Blocked with 404", f"Status: {s}")

    # =========================================================================
    # 5. DASHBOARD, REPORTING & SIMULATOR AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("5. DASHBOARD, REPORTING & SIMULATOR AUDIT")
    print("=" * 50)

    # 5.1 System Model Metrics
    s, r = api_call("GET", "/api/v1/intelligence/metrics")
    assert_test(s == 200 and "xgboost" in r and r.get("xgboost", {}).get("roc_auc") == 1.0,
                "5.1 System Model Intelligence Metrics", f"ROC-AUC: {r.get('xgboost', {}).get('roc_auc')}")

    # 5.2 Global Feature Importances
    s, r = api_call("GET", "/api/v1/intelligence/global-features")
    assert_test(s == 200 and len(r.get("features", [])) >= 5,
                "5.2 Global Feature Importance Attribution", f"Feature count: {len(r.get('features', []))}")

    # 5.3 User Profile Spending Baseline Radar
    s, r = api_call("GET", f"/api/v1/intelligence/user/{identifier_u1}/profile")
    assert_test(s == 200 and "avg_amount_30d" in r and "std_amount_30d" in r,
                "5.3 User Behavioral Baseline Profile", f"Avg: ${r.get('avg_amount_30d')}")

    # 5.4 What-If Scenario Risk Simulator
    sim_data = {
        "baseline_transaction": {"amount": 50.0, "payment_method": "credit_card", "location_city": "Mumbai", "is_device_familiar": True},
        "modified_transaction": {"amount": 5500.0, "payment_method": "credit_card", "location_city": "Dubai", "is_device_familiar": False}
    }
    s, r = api_call("POST", "/api/v1/simulator/evaluate", sim_data)
    assert_test(s == 200 and r.get("score_delta", 0) > 0 and bool(r.get("primary_influencing_change")),
                "5.4 What-If Risk Simulator Delta Evaluation", f"Delta: +{r.get('score_delta')} pts, Primary Driver: {r.get('primary_influencing_change')}")

    # 5.5 Alert Status Triage (PATCH)
    if a_u1:
        alert_id = a_u1[0]["id"]
        s, r = api_call("PATCH", f"/api/v1/alerts/{alert_id}/status", {"status": "RESOLVED", "analyst_notes": "Phase 5 audit verified"})
        assert_test(s == 200 and r.get("new_status") == "RESOLVED" and r.get("success") is True,
                    "5.5 Alert Triage Workflow (OPEN -> RESOLVED)", f"Alert ID: {alert_id}, Status: {r.get('new_status')}")

    # 5.6 Institutional Multi-Transaction PDF Generation
    s, pdf_bytes = api_call("GET", "/api/v1/reports/export/pdf", token=token_u1)
    assert_test(s == 200 and isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF-"),
                "5.6 Institutional Multi-Transaction PDF Export", f"Binary Size: {len(pdf_bytes)} bytes")

    # 5.7 Backend Health Heartbeat
    s, r = api_call("GET", "/health")
    assert_test(s == 200 and r.get("status") in ("ok", "healthy"), "5.7 Health Heartbeat", f"Status: {r.get('status')}")

    # =========================================================================
    # 6. DATABASE INTEGRITY AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("6. DATABASE INTEGRITY AUDIT")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM transactions")
    tx_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM risk_assessments")
    risk_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM alerts")
    alert_count = cur.fetchone()[0]

    assert_test(user_count > 0, "6.1 Users Table Verified", f"Total Users: {user_count}")
    assert_test(tx_count > 0, "6.2 Transactions Table Verified", f"Total Transactions: {tx_count}")
    assert_test(risk_count == tx_count, "6.3 1:1 Transaction-Risk Assessment Integrity", f"Tx: {tx_count}, Risk: {risk_count}")
    assert_test(alert_count > 0, "6.4 Alerts Table Verified", f"Total Alerts: {alert_count}")

    # Check for orphaned records
    cur.execute("SELECT COUNT(*) FROM risk_assessments WHERE transaction_id NOT IN (SELECT id FROM transactions)")
    orphaned_risks = cur.fetchone()[0]
    assert_test(orphaned_risks == 0, "6.5 Zero Orphaned Risk Assessments", "Integrity confirmed")

    cur.execute("SELECT COUNT(*) FROM alerts WHERE transaction_id NOT IN (SELECT id FROM transactions)")
    orphaned_alerts = cur.fetchone()[0]
    assert_test(orphaned_alerts == 0, "6.6 Zero Orphaned Security Alerts", "Integrity confirmed")

    conn.close()

    # Save credentials for post-restart audit
    restart_data = {
        "email_user1": email_user1,
        "pwd_user1": pwd_user1,
        "tx_count": tx_count,
        "u1_high_ref": u1_high_ref
    }
    with open(STATE_FILE, "w") as f:
        json.dump(restart_data, f)

    # =========================================================================
    # FINAL PHASE 5 RESULTS
    # =========================================================================
    print("\n" + "=" * 90)
    print(f"PHASE 5 AUDIT PART 1 RESULTS: {passed_tests} / {total_tests} TESTS PASSED ({passed_tests/total_tests*100:.1f}%)")
    print("=" * 90)
    return passed_tests, total_tests

if __name__ == "__main__":
    run_phase5_master_audit()
