import urllib.request
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def req(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    r = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return resp.status, json.loads(resp.read().decode("utf-8"))
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body_text)
        except Exception:
            return e.code, body_text

print("--- Testing Negative Amount ---")
s, b = req("POST", "/api/v1/transactions/analyze", {"amount": -50.0, "location_city": "Mumbai"})
print(f"Negative amount: Status={s}, Body={b}")

print("--- Testing Zero Amount ---")
s, b = req("POST", "/api/v1/transactions/analyze", {"amount": 0.0, "location_city": "Mumbai"})
print(f"Zero amount: Status={s}, Body={b}")

print("--- Testing Unknown City ---")
s, b = req("POST", "/api/v1/transactions/analyze", {"amount": 45.0, "location_city": "Atlantis", "is_device_familiar": True})
print(f"Unknown city: Status={s}, Score={b.get('overall_risk_score') if isinstance(b, dict) else b}")

print("--- Testing New Device ---")
s, b = req("POST", "/api/v1/transactions/analyze", {"amount": 750.0, "location_city": "Bangalore", "is_device_familiar": False})
print(f"New device: Status={s}, Score={b.get('overall_risk_score') if isinstance(b, dict) else b}")

print("--- Testing Invalid Payment Method ---")
s, b = req("POST", "/api/v1/transactions/analyze", {"amount": 100.0, "payment_method": "invalid_crypto", "location_city": "Mumbai"})
print(f"Invalid payment method: Status={s}, Body={b}")
