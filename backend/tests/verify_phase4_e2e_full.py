import urllib.request
import json
import uuid
import sys
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = Path("backend/transactionguard.db")

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


def run_full_phase4_test_suite():
    print("=" * 90)
    print("PHASE 4: COMPLETE END-TO-END APPLICATION TESTING & FINAL VERIFICATION")
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
    # PART 1: AUTHENTICATION
    # =========================================================================
    print("\n" + "=" * 50)
    print("PART 1: AUTHENTICATION VERIFICATION")
    print("=" * 50)

    email_alpha = f"alpha_{uuid.uuid4().hex[:6]}@transactionguard.ai"
    pwd_alpha = "AlphaPass123!"
    email_beta = f"beta_{uuid.uuid4().hex[:6]}@transactionguard.ai"
    pwd_beta = "BetaPass123!"

    # 1.1 Register User Alpha
    s, r = api_call("POST", "/api/v1/auth/signup", {"email": email_alpha, "password": pwd_alpha, "full_name": "User Alpha"})
    assert_test(s == 201 and "access_token" in r, "1.1 User Alpha Registration", f"Status: {s}, ID: {r.get('user', {}).get('id')}")
    token_alpha = r["access_token"]
    id_alpha = r["user"]["id"]
    identifier_alpha = r["user"]["user_identifier"]

    # 1.2 Duplicate email registration
    s, r = api_call("POST", "/api/v1/auth/signup", {"email": email_alpha, "password": pwd_alpha, "full_name": "User Alpha Duplicate"})
    assert_test(s == 400 and "already exists" in str(r).lower(), "1.2 Duplicate Email Rejection", f"Status: {s}")

    # 1.3 Login with correct credentials
    s, r = api_call("POST", "/api/v1/auth/login", {"email": email_alpha, "password": pwd_alpha})
    assert_test(s == 200 and r.get("user", {}).get("email") == email_alpha, "1.3 Login with Correct Credentials", f"Status: {s}")
    token_alpha = r["access_token"]

    # 1.4 Login with incorrect password
    s, r = api_call("POST", "/api/v1/auth/login", {"email": email_alpha, "password": "WrongPassword999!"})
    assert_test(s == 401 and "invalid" in str(r).lower(), "1.4 Invalid Password Rejection", f"Status: {s}")

    # 1.5 Login with non-existent email
    s, r = api_call("POST", "/api/v1/auth/login", {"email": "nonexistent@transactionguard.ai", "password": pwd_alpha})
    assert_test(s == 401 and "invalid" in str(r).lower(), "1.5 Non-Existent Email Rejection", f"Status: {s}")

    # 1.6 Password length validation (> 72 bytes bcrypt ceiling)
    s, r = api_call("POST", "/api/v1/auth/signup", {"email": f"long_{uuid.uuid4().hex[:6]}@test.com", "password": "A" * 75, "full_name": "Long Pwd"})
    assert_test(s == 422 and "72 bytes" in str(r).lower(), "1.6 Password > 72 Bytes Rejection", f"Status: {s}")

    # 1.7 Session verification (/auth/me)
    s, r = api_call("GET", "/api/v1/auth/me", token=token_alpha)
    assert_test(s == 200 and r.get("id") == id_alpha, "1.7 Profile /auth/me with Bearer Token", f"Email: {r.get('email')}")

    # 1.8 Unauthorized profile access
    s, r = api_call("GET", "/api/v1/auth/me")
    assert_test(s == 401, "1.8 Profile /auth/me without Token", f"Status: {s}")

    # =========================================================================
    # PART 2: REGISTER SECOND ACCOUNT FOR DATA ISOLATION
    # =========================================================================
    print("\n" + "=" * 50)
    print("PART 2: USER DATA ISOLATION SETUP")
    print("=" * 50)

    s, r = api_call("POST", "/api/v1/auth/signup", {"email": email_beta, "password": pwd_beta, "full_name": "User Beta"})
    assert_test(s == 201 and "access_token" in r, "2.1 User Beta Registration", f"Status: {s}, ID: {r.get('user', {}).get('id')}")
    token_beta = r["access_token"]
    id_beta = r["user"]["id"]
    identifier_beta = r["user"]["user_identifier"]

    # =========================================================================
    # PART 3: TRANSACTION ANALYSIS & ML INFERENCE ENGINE
    # =========================================================================
    print("\n" + "=" * 50)
    print("PART 3: TRANSACTION ANALYSIS & RISK ENGINE")
    print("=" * 50)

    # 3.1 Low-Risk Transaction (Alpha)
    tx_low = {
        "amount": 28.50,
        "currency": "USD",
        "payment_method": "credit_card",
        "location_city": "Mumbai",
        "is_device_familiar": True
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_low, token=token_alpha)
    assert_test(s == 200 and r["risk_category"] == "LOW" and r["recommended_action"] == "APPROVE",
                "3.1 Low-Risk Analysis", f"Score: {r['overall_risk_score']}, Category: {r['risk_category']}")
    alpha_low_ref = r["transaction_ref"]

    # 3.2 Medium-Risk Transaction (Alpha, 5 hours later in Bangalore, unfamiliar device, EUR)
    t2_time = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
    tx_med = {
        "amount": 750.00,
        "currency": "EUR",
        "payment_method": "debit_card",
        "location_city": "Bangalore",
        "is_device_familiar": False,
        "transaction_timestamp": t2_time,
        "advanced_details": {"merchant_category": "electronics"}
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_med, token=token_alpha)
    assert_test(s == 200 and r["risk_category"] == "MEDIUM" and r["recommended_action"] == "REVIEW",
                "3.2 Medium-Risk Analysis", f"Score: {r['overall_risk_score']}, Category: {r['risk_category']}")
    alpha_med_ref = r["transaction_ref"]

    # 3.3 High-Risk Transaction (Alpha, Dubai, luxury, unfamiliar device, GBP)
    tx_high = {
        "amount": 9800.00,
        "currency": "GBP",
        "payment_method": "credit_card",
        "location_city": "Dubai",
        "is_device_familiar": False,
        "advanced_details": {"merchant_category": "luxury"}
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_high, token=token_alpha)
    assert_test(s == 200 and r["risk_category"] in ("HIGH", "CRITICAL") and r["recommended_action"] == "BLOCK",
                "3.3 High-Risk Analysis", f"Score: {r['overall_risk_score']}, Category: {r['risk_category']}")
    alpha_high_ref = r["transaction_ref"]

    # 3.4 User Beta: Safe Transaction (INR, upi, Delhi, everyday essentials)
    tx_beta_safe = {
        "amount": 150.00,
        "currency": "INR",
        "payment_method": "upi",
        "location_city": "Delhi",
        "is_device_familiar": True
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_beta_safe, token=token_beta)
    assert_test(s == 200 and r["risk_category"] == "LOW",
                "3.4 User Beta Safe UPI Analysis", f"Score: {r['overall_risk_score']}, Ref: {r['transaction_ref']}")
    beta_safe_ref = r["transaction_ref"]

    # 3.5 User Beta: Impossible Travel (London then Tokyo within 1 second)
    tx_beta_lon = {
        "amount": 90.00,
        "currency": "GBP",
        "payment_method": "credit_card",
        "location_city": "London",
        "is_device_familiar": True
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_beta_lon, token=token_beta)
    assert_test(s == 200, "3.5 User Beta Tx 1 London", f"Ref: {r['transaction_ref']}")

    tx_beta_tokyo = {
        "amount": 6200.00,
        "currency": "USD",
        "payment_method": "credit_card",
        "location_city": "Tokyo",
        "is_device_familiar": False
    }
    s, r = api_call("POST", "/api/v1/transactions/analyze", tx_beta_tokyo, token=token_beta)
    assert_test(s == 200 and "IMPOSSIBLE_TRAVEL_VELOCITY" in r.get("risk_analyst", {}).get("rules_triggered", []) and r["recommended_action"] == "BLOCK",
                "3.6 Impossible Travel Hard Circuit Breaker", f"Score: {r['overall_risk_score']}, Action: {r['recommended_action']}")
    beta_tokyo_ref = r["transaction_ref"]

    # 3.7 Unknown City (Reykjavik)
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 42.00, "location_city": "Reykjavik", "payment_method": "credit_card", "is_device_familiar": True}, token=token_alpha)
    assert_test(s == 200 and "transaction_ref" in r, "3.7 Unknown City Handling", f"Score: {r['overall_risk_score']}, Ref: {r['transaction_ref']}")

    # 3.8 Negative Amount Validation
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": -50.00, "location_city": "Mumbai"}, token=token_alpha)
    assert_test(s == 422 and "greater than 0" in str(r).lower(), "3.8 Negative Amount Rejected with HTTP 422", f"Status: {s}")

    # 3.9 Zero Amount Validation
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 0.00, "location_city": "Mumbai"}, token=token_alpha)
    assert_test(s == 422 and "greater than 0" in str(r).lower(), "3.9 Zero Amount Rejected with HTTP 422", f"Status: {s}")

    # 3.10 Ceiling Limit Validation ($100,000,001)
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 100_000_001.0, "location_city": "Mumbai"}, token=token_alpha)
    assert_test(s == 422 and "ceiling" in str(r).lower(), "3.10 Amount > $100M Rejected with HTTP 422", f"Status: {s}")

    # 3.11 Invalid Payment Method
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 50.00, "payment_method": "crypto_token", "location_city": "Mumbai"}, token=token_alpha)
    assert_test(s == 422 and "supported payment methods" in str(r).lower(), "3.11 Invalid Payment Method Rejected with HTTP 422", f"Status: {s}")

    # 3.12 Invalid Currency Code
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 50.00, "currency": "FAKECURR", "location_city": "Mumbai"}, token=token_alpha)
    assert_test(s == 422 and "supported currencies" in str(r).lower(), "3.12 Invalid Currency Rejected with HTTP 422", f"Status: {s}")

    # 3.13 Empty City
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 50.00, "location_city": "   "}, token=token_alpha)
    assert_test(s == 422 and "city cannot be empty" in str(r).lower(), "3.13 Empty City Rejected with HTTP 422", f"Status: {s}")

    # 3.14 Verify Real ML Model Artifacts & Diagnostics
    s, r = api_call("POST", "/api/v1/transactions/analyze", {"amount": 500.0, "payment_method": "credit_card", "location_city": "Mumbai", "is_device_familiar": True}, token=token_alpha)
    diag = r.get("risk_analyst", {}).get("model_signals", {})
    shap_list = r.get("risk_analyst", {}).get("top_shap_contributions", [])
    has_real_ml = (
        0.0 <= diag.get("xgb_fraud_probability", -1) <= 1.0 and
        0.0 <= diag.get("iforest_anomaly_score", -1) <= 100.0 and
        len(shap_list) >= 3 and
        all("shap_value" in item and "display_name" in item for item in shap_list)
    )
    assert_test(has_real_ml, "3.14 Real ML Diagnostics Verification",
                f"XGB P(Fraud)={diag.get('xgb_fraud_probability')}, IForest={diag.get('iforest_anomaly_score')}, SHAP count={len(shap_list)}")

    # =========================================================================
    # PART 4: USER DATA ISOLATION VERIFICATION
    # =========================================================================
    print("\n" + "=" * 50)
    print("PART 4: USER DATA ISOLATION ENFORCEMENT")
    print("=" * 50)

    # 4.1 Past Transactions Isolation
    s, r_alpha = api_call("GET", "/api/v1/transactions/history", token=token_alpha)
    alpha_refs = [x["transaction_ref"] for x in r_alpha["records"]]
    s, r_beta = api_call("GET", "/api/v1/transactions/history", token=token_beta)
    beta_refs = [x["transaction_ref"] for x in r_beta["records"]]

    assert_test(alpha_high_ref in alpha_refs and alpha_high_ref not in beta_refs,
                "4.1 Alpha Transactions Isolated from Beta", f"Alpha Total: {len(alpha_refs)}")
    assert_test(beta_tokyo_ref in beta_refs and beta_tokyo_ref not in alpha_refs,
                "4.2 Beta Transactions Isolated from Alpha", f"Beta Total: {len(beta_refs)}")

    # 4.2 Alerts Feed Isolation
    s, alerts_alpha = api_call("GET", "/api/v1/alerts/feed", token=token_alpha)
    alpha_alert_refs = [a["transaction_ref"] for a in alerts_alpha]
    s, alerts_beta = api_call("GET", "/api/v1/alerts/feed", token=token_beta)
    beta_alert_refs = [a["transaction_ref"] for a in alerts_beta]

    assert_test(alpha_high_ref in alpha_alert_refs and alpha_high_ref not in beta_alert_refs,
                "4.3 Alpha Security Alerts Isolated", f"Alpha Alerts: {len(alpha_alert_refs)}")
    assert_test(beta_tokyo_ref in beta_alert_refs and beta_tokyo_ref not in alpha_alert_refs,
                "4.4 Beta Security Alerts Isolated", f"Beta Alerts: {len(beta_alert_refs)}")

    # 4.3 CSV Export Isolation
    s, csv_alpha = api_call("GET", "/api/v1/reports/export/csv", token=token_alpha)
    csv_alpha_str = csv_alpha.decode("utf-8") if isinstance(csv_alpha, bytes) else str(csv_alpha)
    s, csv_beta = api_call("GET", "/api/v1/reports/export/csv", token=token_beta)
    csv_beta_str = csv_beta.decode("utf-8") if isinstance(csv_beta, bytes) else str(csv_beta)

    assert_test(alpha_high_ref in csv_alpha_str and beta_tokyo_ref not in csv_alpha_str,
                "4.5 Alpha CSV Export Scoped Strictly", "Alpha CSV contains 0 Beta records")
    assert_test(beta_tokyo_ref in csv_beta_str and alpha_high_ref not in csv_beta_str,
                "4.6 Beta CSV Export Scoped Strictly", "Beta CSV contains 0 Alpha records")

    # 4.4 Cross-User Single PDF Download Blocked
    s, r = api_call("GET", f"/api/v1/reports/export/pdf/{beta_tokyo_ref}", token=token_alpha)
    assert_test(s == 404, "4.7 Unauthorized PDF Export Blocked with HTTP 404", f"Status: {s}")

    # =========================================================================
    # PART 5: DASHBOARD, RISK INSIGHTS, SIMULATOR & REPORTS APIS
    # =========================================================================
    print("\n" + "=" * 50)
    print("PART 5: DASHBOARD & REPORTING APIS")
    print("=" * 50)

    # 5.1 Intelligence Metrics
    s, r = api_call("GET", "/api/v1/intelligence/metrics")
    assert_test(s == 200 and "xgboost" in r and "training_samples" in r,
                "5.1 Model Evaluation Metrics Endpoint", f"ROC-AUC: {r.get('xgboost', {}).get('roc_auc')}")

    # 5.2 Global Feature Importance
    s, r = api_call("GET", "/api/v1/intelligence/global-features")
    assert_test(s == 200 and "features" in r and len(r["features"]) > 0,
                "5.2 Global Feature Importance Endpoint", f"Top feature: {r['features'][0]['feature']}")

    # 5.3 User Behavioral Baseline
    s, r = api_call("GET", f"/api/v1/intelligence/user/{identifier_alpha}/profile")
    print(f"5.3 Status: {s}, Body: {r}")
    assert_test(s == 200 and isinstance(r, dict) and "avg_amount_30d" in r,
                "5.3 User Baseline Radar Profile Endpoint", f"Avg: ${r.get('avg_amount_30d') if isinstance(r, dict) else r}")

    # 5.4 What-If Risk Simulator
    sim_payload = {
        "baseline_transaction": {
            "amount": 50.0,
            "payment_method": "credit_card",
            "location_city": "Mumbai",
            "is_device_familiar": True
        },
        "modified_transaction": {
            "amount": 4500.0,
            "payment_method": "credit_card",
            "location_city": "Dubai",
            "is_device_familiar": False
        }
    }
    s, r = api_call("POST", "/api/v1/simulator/evaluate", sim_payload)
    assert_test(s == 200 and r.get("score_delta", 0) > 0 and "primary_influencing_change" in r,
                "5.4 What-If Simulator Endpoint", f"Delta: +{r.get('score_delta')} pts, Influencing: {r.get('primary_influencing_change')}")

    # 5.5 Alert Status Triage (PATCH)
    if alerts_alpha:
        alert_id = alerts_alpha[0]["id"]
        s, r = api_call("PATCH", f"/api/v1/alerts/{alert_id}/status", {"status": "RESOLVED", "analyst_notes": "Verified by fraud team"})
        assert_test(s == 200 and r.get("new_status") == "RESOLVED" and r.get("success") is True,
                    "5.5 Alert Status Update (OPEN -> RESOLVED)", f"Alert ID: {alert_id}, Status: {r.get('new_status')}")

    # 5.6 Institutional PDF Generation (Multi-Tx)
    s, pdf_bytes = api_call("GET", "/api/v1/reports/export/pdf", token=token_alpha)
    assert_test(s == 200 and isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF-"),
                "5.6 Institutional Multi-Tx PDF Export", f"Bytes generated: {len(pdf_bytes)}")

    # 5.7 Health Heartbeat
    s, r = api_call("GET", "/health")
    assert_test(s == 200 and r.get("status") in ("ok", "healthy"), "5.7 Backend System Health Heartbeat", f"Status: {s}")

    # =========================================================================
    # PART 6: DATABASE RELATIONSHIPS & PERSISTENCE INTEGRITY
    # =========================================================================
    print("\n" + "=" * 50)
    print("PART 6: DATABASE RELATIONSHIPS & PERSISTENCE INTEGRITY")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 6.1 User Ownership Foreign Keys
    cur.execute("SELECT COUNT(*) FROM transactions WHERE user_id IS NULL")
    anonymous_txs = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (id_alpha,))
    alpha_db_txs = cur.fetchone()[0]
    assert_test(alpha_db_txs >= 4, "6.1 Foreign Key Transaction.user_id Persistence", f"User Alpha txs in SQLite: {alpha_db_txs}")

    # 6.2 Risk Assessments Foreign Keys (1-to-1)
    cur.execute("SELECT COUNT(*) FROM risk_assessments WHERE transaction_id NOT IN (SELECT id FROM transactions)")
    orphaned_risks = cur.fetchone()[0]
    assert_test(orphaned_risks == 0, "6.2 Zero Orphaned Risk Assessments", f"Orphan count: {orphaned_risks}")

    # 6.3 Alerts Foreign Keys
    cur.execute("SELECT COUNT(*) FROM alerts WHERE transaction_id NOT IN (SELECT id FROM transactions)")
    orphaned_alerts = cur.fetchone()[0]
    assert_test(orphaned_alerts == 0, "6.3 Zero Orphaned Security Alerts", f"Orphan count: {orphaned_alerts}")

    # 6.4 Session Persistence across re-login
    s, login_r = api_call("POST", "/api/v1/auth/login", {"email": email_alpha, "password": pwd_alpha})
    assert_test(s == 200, "6.4 Re-Login after session cycle", f"New Token issued: {bool(login_r.get('access_token'))}")
    re_token = login_r["access_token"]
    s, hist_re = api_call("GET", "/api/v1/transactions/history", token=re_token)
    assert_test(s == 200 and len(hist_re["records"]) >= 4, "6.5 History Intact Across Re-Login", f"Records found: {len(hist_re['records'])}")

    conn.close()

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "=" * 90)
    print(f"PHASE 4 E2E TEST RESULTS: {passed_tests} / {total_tests} TESTS PASSED ({passed_tests/total_tests*100:.1f}%)")
    print("=" * 90)

    if passed_tests == total_tests:
        print(">>> ALL PHASE 4 END-TO-END VERIFICATION TESTS PASSED WITH ZERO FAILURES! <<<")
    else:
        print(f">>> {total_tests - passed_tests} TESTS FAILED <<<")

if __name__ == "__main__":
    run_full_phase4_test_suite()
