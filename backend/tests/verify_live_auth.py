import urllib.request
import json
import uuid
import sys

BASE_URL = "http://127.0.0.1:8000"

def make_request(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed

def run_tests():
    print("=" * 60)
    print("LIVE AUTHENTICATION API TEST SUITE")
    print(f"Target: {BASE_URL}")
    print("=" * 60)

    # 1. Signup test (New User)
    print("\n--- Test 1: User Registration (Signup) ---")
    unique_email = f"live_verify_{uuid.uuid4().hex[:6]}@transactionguard.ai"
    signup_payload = {
        "email": unique_email,
        "password": "SecurePassword123!",
        "full_name": "Verification Analyst"
    }
    code, data = make_request("POST", "/api/v1/auth/signup", signup_payload)
    print(f"Status Code: {code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    assert code == 201, f"Expected 201, got {code}"
    assert "access_token" in data, "Token missing from signup response"
    assert data.get("token_type") == "bearer", "Token type must be 'bearer'"
    assert data["user"]["email"] == unique_email
    assert data["user"]["full_name"] == "Verification Analyst"
    jwt_token = data["access_token"]
    user_id = data["user"]["id"]
    print("Result: PASSED (HTTP 201 Created with valid JWT)")

    # 2. Duplicate Email Registration Test
    print("\n--- Test 2: Duplicate Email Registration ---")
    dup_code, dup_data = make_request("POST", "/api/v1/auth/signup", signup_payload)
    print(f"Status Code: {dup_code}")
    print(f"Response: {json.dumps(dup_data, indent=2)}")
    assert dup_code == 400, f"Expected 400, got {dup_code}"
    assert "already exists" in dup_data.get("detail", "").lower(), "Expected duplicate email error message"
    print("Result: PASSED (HTTP 400 Bad Request returned as expected)")

    # 3. Login with Valid Credentials
    print("\n--- Test 3: Login with Valid Credentials ---")
    login_payload = {
        "email": unique_email,
        "password": "SecurePassword123!"
    }
    log_code, log_data = make_request("POST", "/api/v1/auth/login", login_payload)
    print(f"Status Code: {log_code}")
    print(f"Response: {json.dumps(log_data, indent=2)}")
    assert log_code == 200, f"Expected 200, got {log_code}"
    assert "access_token" in log_data
    assert log_data["user"]["email"] == unique_email
    login_token = log_data["access_token"]
    print("Result: PASSED (HTTP 200 OK with Bearer access token)")

    # 4. Login with Invalid Password
    print("\n--- Test 4: Login with Invalid Password ---")
    bad_login_payload = {
        "email": unique_email,
        "password": "IncorrectPassword999!"
    }
    bad_code, bad_data = make_request("POST", "/api/v1/auth/login", bad_login_payload)
    print(f"Status Code: {bad_code}")
    print(f"Response: {json.dumps(bad_data, indent=2)}")
    assert bad_code == 401, f"Expected 401, got {bad_code}"
    assert "invalid" in bad_data.get("detail", "").lower(), "Expected invalid credentials error message"
    print("Result: PASSED (HTTP 401 Unauthorized returned as expected)")

    # 5. User Profile API (/api/v1/auth/me) with Authenticated Token
    print("\n--- Test 5: User Profile API (/auth/me) with Token ---")
    me_code, me_data = make_request("GET", "/api/v1/auth/me", token=login_token)
    print(f"Status Code: {me_code}")
    print(f"Response: {json.dumps(me_data, indent=2)}")
    assert me_code == 200, f"Expected 200, got {me_code}"
    assert me_data["id"] == user_id
    assert me_data["email"] == unique_email
    assert me_data["full_name"] == "Verification Analyst"
    print("Result: PASSED (HTTP 200 OK with accurate profile details)")

    # 6. Unauthorized User Profile API (/api/v1/auth/me) without Token
    print("\n--- Test 6: Unauthorized User Profile API (/auth/me) without Token ---")
    unauth_code, unauth_data = make_request("GET", "/api/v1/auth/me")
    print(f"Status Code: {unauth_code}")
    print(f"Response: {json.dumps(unauth_data, indent=2)}")
    assert unauth_code == 401, f"Expected 401, got {unauth_code}"
    print("Result: PASSED (HTTP 401 Unauthorized returned as expected)")

    print("\n" + "=" * 60)
    print("ALL 6 LIVE AUTHENTICATION TESTS PASSED WITH ZERO ERRORS!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
