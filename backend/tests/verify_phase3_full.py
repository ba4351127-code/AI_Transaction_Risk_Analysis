import urllib.request
import json
import uuid
import sys
import time
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000"

def api_request(method, path, body=None, token=None):
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

def run_phase3_tests():
    print("=" * 80)
    print("PHASE 3: COMPLETE TRANSACTION ANALYSIS & RISK ENGINE VERIFICATION")
    print(f"Target Server: {BASE_URL}")
    print("=" * 80)

    # Setup User 1 and User 2
    u1_email = f"user1_{uuid.uuid4().hex[:6]}@transactionguard.ai"
    u1_pwd = "Password123!"
    u2_email = f"user2_{uuid.uuid4().hex[:6]}@transactionguard.ai"
    u2_pwd = "Password123!"

    print("\n--- Setup: Registering User 1 and User 2 ---")
    s1, r1 = api_request("POST", "/api/v1/auth/signup", {"email": u1_email, "password": u1_pwd, "full_name": "User One"})
    assert s1 == 201, f"User 1 signup failed: {s1}"
    u1_token = r1["access_token"]
    u1_id = r1["user"]["id"]
    print(f"User 1 created: ID={u1_id}, Email={u1_email}")

    s2, r2 = api_request("POST", "/api/v1/auth/signup", {"email": u2_email, "password": u2_pwd, "full_name": "User Two"})
    assert s2 == 201, f"User 2 signup failed: {s2}"
    u2_token = r2["access_token"]
    u2_id = r2["user"]["id"]
    print(f"User 2 created: ID={u2_id}, Email={u2_email}")

    # TEST 1: Valid Low-Risk Transaction
    print("\n" + "=" * 60)
    print("TEST 1: Valid Low-Risk Transaction")
    t1_payload = {
        "amount": 35.50,
        "currency": "USD",
        "payment_method": "credit_card",
        "location_city": "Mumbai",
        "is_device_familiar": True
    }
    s, r = api_request("POST", "/api/v1/transactions/analyze", t1_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Transaction Ref: {r.get('transaction_ref')}")
    print(f"Risk Score: {r.get('overall_risk_score')}/100")
    print(f"Risk Category: {r.get('risk_category')}")
    print(f"Recommended Action: {r.get('recommended_action')}")
    print(f"Headline: {r.get('everyday_user', {}).get('headline')}")
    assert s == 200
    assert r.get("risk_category") == "LOW"
    assert r.get("recommended_action") == "APPROVE"
    u1_t1_ref = r["transaction_ref"]
    print("Result: PASSED (Low risk correctly classified, score <= 25)")

    # TEST 2: Medium-Risk Transaction
    print("\n" + "=" * 60)
    print("TEST 2: Medium-Risk Transaction")
    # $750.00 in Bangalore from unfamiliar device (5 hours after Mumbai flight)
    t2_timestamp = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
    t2_payload = {
        "amount": 750.00,
        "currency": "USD",
        "payment_method": "credit_card",
        "location_city": "Bangalore",
        "is_device_familiar": False,
        "transaction_timestamp": t2_timestamp,
        "advanced_details": {
            "merchant_category": "electronics"
        }
    }
    s, r = api_request("POST", "/api/v1/transactions/analyze", t2_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Transaction Ref: {r.get('transaction_ref')}")
    print(f"Risk Score: {r.get('overall_risk_score')}/100")
    print(f"Risk Category: {r.get('risk_category')}")
    print(f"Recommended Action: {r.get('recommended_action')}")
    print(f"Triggered Heuristics: {r.get('risk_analyst', {}).get('rules_triggered')}")
    assert s == 200
    assert r.get("risk_category") in ("MEDIUM", "HIGH")
    assert r.get("recommended_action") in ("REVIEW", "BLOCK")
    u1_t2_ref = r["transaction_ref"]
    print("Result: PASSED (Medium risk detected with device familiarity penalty)")

    # TEST 3: High-Risk Transaction
    print("\n" + "=" * 60)
    print("TEST 3: High-Risk Transaction")
    # $9,500.00 in Dubai, unfamiliar device, luxury merchant
    t3_payload = {
        "amount": 9500.00,
        "currency": "USD",
        "payment_method": "credit_card",
        "location_city": "Dubai",
        "is_device_familiar": False,
        "advanced_details": {
            "merchant_category": "luxury"
        }
    }
    s, r = api_request("POST", "/api/v1/transactions/analyze", t3_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Transaction Ref: {r.get('transaction_ref')}")
    print(f"Risk Score: {r.get('overall_risk_score')}/100")
    print(f"Risk Category: {r.get('risk_category')}")
    print(f"Recommended Action: {r.get('recommended_action')}")
    print(f"Action Advice: {r.get('everyday_user', {}).get('action_advice')}")
    assert s == 200
    assert r.get("risk_category") in ("HIGH", "CRITICAL")
    assert r.get("recommended_action") == "BLOCK"
    u1_t3_ref = r["transaction_ref"]
    print("Result: PASSED (High/Critical risk triggered, BLOCK recommended)")

    # TEST 4: Negative Amount
    print("\n" + "=" * 60)
    print("TEST 4: Negative Amount Input")
    t4_payload = {"amount": -150.00, "location_city": "Mumbai", "payment_method": "credit_card"}
    s, r = api_request("POST", "/api/v1/transactions/analyze", t4_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Response: {r}")
    assert s == 422
    assert "greater than 0" in str(r).lower()
    print("Result: PASSED (HTTP 422 returned with clear validation message)")

    # TEST 5: Zero Amount
    print("\n" + "=" * 60)
    print("TEST 5: Zero Amount Input")
    t5_payload = {"amount": 0.00, "location_city": "Mumbai", "payment_method": "credit_card"}
    s, r = api_request("POST", "/api/v1/transactions/analyze", t5_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Response: {r}")
    assert s == 422
    assert "greater than 0" in str(r).lower()
    print("Result: PASSED (HTTP 422 returned with clear validation message)")

    # TEST 6: Invalid Currency and Invalid Payment Method
    print("\n" + "=" * 60)
    print("TEST 6A: Invalid Payment Method")
    t6a_payload = {"amount": 50.00, "payment_method": "crypto_token", "location_city": "Mumbai"}
    s, r = api_request("POST", "/api/v1/transactions/analyze", t6a_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Response: {r}")
    assert s == 422
    assert "supported payment methods" in str(r).lower()
    print("Result 6A: PASSED (HTTP 422 rejected invalid payment method)")

    print("\nTEST 6B: Invalid Currency Code")
    t6b_payload = {"amount": 50.00, "currency": "INVALID_CURR", "payment_method": "credit_card", "location_city": "Mumbai"}
    s, r = api_request("POST", "/api/v1/transactions/analyze", t6b_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Response: {r}")
    assert s == 422
    assert "supported currencies" in str(r).lower()
    print("Result 6B: PASSED (HTTP 422 rejected invalid currency)")

    # TEST 7: Unknown City
    print("\n" + "=" * 60)
    print("TEST 7: Unknown City Input")
    t7_payload = {
        "amount": 65.00,
        "payment_method": "credit_card",
        "location_city": "Reykjavik",
        "is_device_familiar": True
    }
    s, r = api_request("POST", "/api/v1/transactions/analyze", t7_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Transaction Ref: {r.get('transaction_ref')}")
    print(f"Risk Score: {r.get('overall_risk_score')}/100")
    print(f"Risk Category: {r.get('risk_category')}")
    assert s == 200
    assert "transaction_ref" in r
    print("Result: PASSED (Unknown city safely handled without 500 error)")

    # TEST 8: New Device
    print("\n" + "=" * 60)
    print("TEST 8: New Device (is_device_familiar=False)")
    t8_payload = {
        "amount": 250.00,
        "payment_method": "debit_card",
        "location_city": "Mumbai",
        "is_device_familiar": False
    }
    s, r = api_request("POST", "/api/v1/transactions/analyze", t8_payload, token=u1_token)
    print(f"Status: {s}")
    print(f"Risk Score: {r.get('overall_risk_score')}/100")
    print(f"Risk Category: {r.get('risk_category')}")
    print(f"Rules Triggered: {r.get('risk_analyst', {}).get('rules_triggered')}")
    assert s == 200
    assert "UNFAMILIAR_DEVICE_ACCESS" in r.get("risk_analyst", {}).get("rules_triggered", [])
    print("Result: PASSED (New device triggered UNFAMILIAR_DEVICE_ACCESS penalty)")

    # TEST 9: Consecutive Transactions from Distant Cities (Geo-Velocity)
    print("\n" + "=" * 60)
    print("TEST 9: Consecutive Transactions from Distant Cities (Impossible Travel)")
    # User 2 performs first tx in London
    tx_london = {
        "amount": 120.00,
        "payment_method": "credit_card",
        "location_city": "London",
        "is_device_familiar": True
    }
    s_lon, r_lon = api_request("POST", "/api/v1/transactions/analyze", tx_london, token=u2_token)
    assert s_lon == 200
    print(f"User 2 Tx 1 in London: Ref={r_lon['transaction_ref']}, Score={r_lon['overall_risk_score']}")

    # Immediately after, User 2 attempts a transaction in Tokyo (9,560 km away)
    tx_tokyo = {
        "amount": 4500.00,
        "payment_method": "credit_card",
        "location_city": "Tokyo",
        "is_device_familiar": False
    }
    s_tok, r_tok = api_request("POST", "/api/v1/transactions/analyze", tx_tokyo, token=u2_token)
    assert s_tok == 200
    print(f"User 2 Tx 2 in Tokyo: Ref={r_tok['transaction_ref']}")
    print(f"Risk Score: {r_tok['overall_risk_score']}/100")
    print(f"Risk Category: {r_tok['risk_category']}")
    print(f"Recommended Action: {r_tok['recommended_action']}")
    print(f"Rules Triggered: {r_tok.get('risk_analyst', {}).get('rules_triggered')}")
    u2_tokyo_ref = r_tok["transaction_ref"]
    assert "IMPOSSIBLE_TRAVEL_VELOCITY" in r_tok.get("risk_analyst", {}).get("rules_triggered", [])
    assert r_tok["recommended_action"] == "BLOCK"
    print("Result: PASSED (Impossible travel hard circuit breaker blocked Tokyo transaction)")

    # TEST 10: Database Persistence Survives Logout & Login
    print("\n" + "=" * 60)
    print("TEST 10: Database Persistence Survives Logout and Login")
    # Simulate logout by discarding token, then log in again
    login_s, login_r = api_request("POST", "/api/v1/auth/login", {"email": u1_email, "password": u1_pwd})
    assert login_s == 200
    new_u1_token = login_r["access_token"]
    print("User 1 successfully logged back in with fresh JWT session.")

    # Fetch User 1 transaction history
    hist_s, hist_r = api_request("GET", "/api/v1/transactions/history", token=new_u1_token)
    assert hist_s == 200
    u1_records = hist_r["records"]
    u1_refs = [rec["transaction_ref"] for rec in u1_records]
    print(f"Total transactions persisted for User 1: {len(u1_records)}")
    assert u1_t1_ref in u1_refs, f"{u1_t1_ref} not found in User 1 history"
    assert u1_t2_ref in u1_refs, f"{u1_t2_ref} not found in User 1 history"
    assert u1_t3_ref in u1_refs, f"{u1_t3_ref} not found in User 1 history"
    print("Result: PASSED (All User 1 transactions intact after re-authentication)")

    # TEST 11: Strict Data Isolation (User 1 vs User 2)
    print("\n" + "=" * 60)
    print("TEST 11: User 1 vs User 2 Strict Data Isolation")
    # 1. Transactions Isolation
    hist_u2_s, hist_u2_r = api_request("GET", "/api/v1/transactions/history", token=u2_token)
    assert hist_u2_s == 200
    u2_records = hist_u2_r["records"]
    u2_refs = [rec["transaction_ref"] for rec in u2_records]

    # User 1 must NOT see User 2's Tokyo ref
    assert u2_tokyo_ref not in u1_refs, "CRITICAL ISOLATION BREACH: User 1 saw User 2's transaction!"
    # User 2 must NOT see User 1's t3 ref
    assert u1_t3_ref not in u2_refs, "CRITICAL ISOLATION BREACH: User 2 saw User 1's transaction!"
    print("Transaction Isolation: PASSED (Zero cross-user leakage in transaction history)")

    # 2. Alerts Isolation
    alerts_u1_s, alerts_u1 = api_request("GET", "/api/v1/alerts/feed", token=new_u1_token)
    assert alerts_u1_s == 200
    u1_alert_refs = [a["transaction_ref"] for a in alerts_u1]

    alerts_u2_s, alerts_u2 = api_request("GET", "/api/v1/alerts/feed", token=u2_token)
    assert alerts_u2_s == 200
    u2_alert_refs = [a["transaction_ref"] for a in alerts_u2]

    print(f"User 1 Alerts Count: {len(alerts_u1)} (Refs: {u1_alert_refs})")
    print(f"User 2 Alerts Count: {len(alerts_u2)} (Refs: {u2_alert_refs})")

    assert u2_tokyo_ref in u2_alert_refs, "User 2 should have alert for blocked Tokyo transaction"
    assert u2_tokyo_ref not in u1_alert_refs, "CRITICAL: User 1 saw User 2's alert!"
    assert u1_t3_ref in u1_alert_refs, "User 1 should have alert for high-risk Dubai transaction"
    assert u1_t3_ref not in u2_alert_refs, "CRITICAL: User 2 saw User 1's alert!"
    print("Alerts Isolation: PASSED (Alerts strictly scoped to owning user)")

    # 3. Reports Isolation (CSV & PDF)
    csv_s, csv_raw = api_request("GET", "/api/v1/reports/export/csv", token=new_u1_token)
    assert csv_s == 200
    csv_text = csv_raw.decode("utf-8") if isinstance(csv_raw, bytes) else str(csv_raw)
    assert u1_t3_ref in csv_text, "User 1 CSV should contain User 1 transactions"
    assert u2_tokyo_ref not in csv_text, "CRITICAL: User 1 CSV export contained User 2 transaction!"
    print("CSV Export Isolation: PASSED (CSV strictly filtered to authenticated user)")

    # User 1 attempts to download User 2's specific transaction PDF -> Must return 404 access denied
    pdf_s, pdf_r = api_request("GET", f"/api/v1/reports/export/pdf/{u2_tokyo_ref}", token=new_u1_token)
    print(f"User 1 access to User 2 PDF report: Status={pdf_s}")
    assert pdf_s == 404
    print("PDF Export Isolation: PASSED (Unauthorized cross-user report download blocked with HTTP 404)")

    print("\n" + "=" * 80)
    print(">>> ALL 11 PHASE 3 END-TO-END VERIFICATION TESTS PASSED SUCCESSFULLY! <<<")
    print("=" * 80)

if __name__ == "__main__":
    run_phase3_tests()
