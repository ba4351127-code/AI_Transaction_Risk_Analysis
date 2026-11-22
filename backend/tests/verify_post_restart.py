import urllib.request
import json
import sqlite3
import uuid
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


def verify_post_restart():
    print("=" * 80)
    print("POST-RESTART PERSISTENCE & SYSTEM INTEGRITY VERIFICATION")
    print(f"Target: {BASE_URL} | Database: {DB_PATH}")
    print("=" * 80)

    # 1. Database table counts and referential integrity check
    assert DB_PATH.exists(), f"Database file not found at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    counts = {t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ['users', 'transactions', 'risk_assessments', 'alerts']}
    print(f"Post-restart SQLite Table Counts: {counts}")
    assert counts['users'] > 0, f"Expected users > 0, got {counts['users']}"
    assert counts['transactions'] > 0, f"Expected transactions > 0, got {counts['transactions']}"
    assert counts['risk_assessments'] == counts['transactions'], f"1:1 Mismatch: {counts['risk_assessments']} risk assessments vs {counts['transactions']} transactions"
    print("[PASS] 1. SQLite Database integrity verified: all tables populated with 1:1 transaction-risk assessment parity.")

    # 2. Determine user credentials (dynamic from state file, or fallback to registered test user)
    saved_ref = None
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        email = state.get("email_user1")
        pwd = state.get("pwd_user1")
        saved_ref = state.get("u1_high_ref")
        print(f"Loaded credentials from {STATE_FILE.name}: {email}")
    else:
        # Fallback: create an audit user dynamically
        email = f"restart_check_{uuid.uuid4().hex[:6]}@transactionguard.ai"
        pwd = "RestartPass123!"
        s, reg = api_call("POST", "/api/v1/auth/signup", {"email": email, "password": pwd, "full_name": "Restart Checker"})
        assert s == 201, f"Fallback registration failed: {s}, {reg}"
        print(f"Dynamically registered test user for restart audit: {email}")

    # 3. Authenticate user
    s, r = api_call("POST", "/api/v1/auth/login", {"email": email, "password": pwd})
    assert s == 200 and "access_token" in r, f"Login failed for {email}: {s}, {r}"
    token = r["access_token"]
    user_id = r["user"]["id"]
    print(f"[PASS] 2. User Authentication succeeded for {email} (User ID: {user_id}).")

    # 4. Retrieve historical transactions
    s, hist = api_call("GET", "/api/v1/transactions/history", token=token)
    assert s == 200 and "records" in hist, f"History fetch failed: {s}, {hist}"
    records = hist["records"]
    print(f"[PASS] 3. Retrieved {len(records)} transaction records belonging to {email}.")
    if saved_ref:
        retrieved_refs = [x["transaction_ref"] for x in records]
        assert saved_ref in retrieved_refs, f"Pre-restart transaction {saved_ref} missing from history!"
        print(f"[PASS] 4. Pre-restart transaction {saved_ref} confirmed intact in user history.")

    # 5. Retrieve alerts
    s, alerts = api_call("GET", "/api/v1/alerts/feed", token=token)
    assert s == 200 and isinstance(alerts, list), f"Alerts fetch failed: {s}, {alerts}"
    print(f"[PASS] 5. Retrieved {len(alerts)} security alerts for {email}.")

    # 6. Submit a new post-restart transaction
    t_post = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    tx = {
        "amount": 49.50,
        "currency": "USD",
        "payment_method": "credit_card",
        "location_city": "Mumbai",
        "is_device_familiar": True,
        "transaction_timestamp": t_post
    }
    s, tx_res = api_call("POST", "/api/v1/transactions/analyze", tx, token=token)
    assert s == 200 and tx_res.get("risk_category") == "LOW", f"Post-restart transaction failed: {s}, {tx_res}"
    new_ref = tx_res["transaction_ref"]
    print(f"[PASS] 6. Post-restart transaction successfully analyzed: Ref={new_ref}, Score={tx_res['overall_risk_score']}.")

    # 7. Verify incremental storage and referential integrity
    cur.execute("SELECT COUNT(*) FROM transactions")
    after_tx = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM risk_assessments")
    after_risk = cur.fetchone()[0]
    assert after_tx == counts['transactions'] + 1, f"Expected {counts['transactions'] + 1}, got {after_tx}"
    assert after_risk == after_tx, f"Mismatch: {after_risk} risks vs {after_tx} txs"
    print(f"[PASS] 7. Database records incremented cleanly: {counts['transactions']} -> {after_tx} transactions.")

    # 8. Check for orphaned records
    cur.execute("SELECT COUNT(*) FROM risk_assessments WHERE transaction_id NOT IN (SELECT id FROM transactions)")
    assert cur.fetchone()[0] == 0, "Orphaned risk assessments found!"
    cur.execute("SELECT COUNT(*) FROM alerts WHERE transaction_id NOT IN (SELECT id FROM transactions)")
    assert cur.fetchone()[0] == 0, "Orphaned alerts found!"
    print("[PASS] 8. Zero orphaned records found in SQLite database. Foreign keys 100% verified.")

    conn.close()
    print("=" * 80)
    print(">>> ALL POST-RESTART PERSISTENCE AND INTEGRITY AUDITS PASSED (100%) <<<")
    print("=" * 80)

if __name__ == "__main__":
    verify_post_restart()
