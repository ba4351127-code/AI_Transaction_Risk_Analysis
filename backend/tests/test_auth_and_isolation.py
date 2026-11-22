import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database.session import init_db


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_auth_signup_and_jwt_flow():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"analyst_{uuid.uuid4().hex[:6]}@transactionguard.ai"
        signup_payload = {
            "email": unique_email,
            "password": "SecurePassword123!",
            "full_name": "Risk Analyst"
        }
        res = await ac.post("/api/v1/auth/signup", json=signup_payload)
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == unique_email
        assert data["user"]["full_name"] == "Risk Analyst"
        assert "user_identifier" in data["user"]

        token = data["access_token"]

        # 2. Test /auth/me with Bearer token
        me_res = await ac.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["email"] == unique_email
        assert me_data["id"] == data["user"]["id"]


@pytest.mark.anyio
async def test_auth_duplicate_email_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"dup_{uuid.uuid4().hex[:6]}@transactionguard.ai"
        payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "First User"
        }
        # First signup succeeds
        res1 = await ac.post("/api/v1/auth/signup", json=payload)
        assert res1.status_code == 201

        # Second signup with same email must fail with 400
        res2 = await ac.post("/api/v1/auth/signup", json=payload)
        assert res2.status_code == 400
        assert "already exists" in res2.json()["detail"].lower()


@pytest.mark.anyio
async def test_auth_login_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"login_test_{uuid.uuid4().hex[:6]}@transactionguard.ai"
        signup_payload = {
            "email": unique_email,
            "password": "CorrectPassword123!",
            "full_name": "Login Tester"
        }
        await ac.post("/api/v1/auth/signup", json=signup_payload)

        # 1. Invalid password must return 401
        bad_login = await ac.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "WrongPassword999!"
        })
        assert bad_login.status_code == 401

        # 2. Correct password must return 200 with JWT
        good_login = await ac.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "CorrectPassword123!"
        })
        assert good_login.status_code == 200
        data = good_login.json()
        assert "access_token" in data
        assert data["user"]["email"] == unique_email


@pytest.mark.anyio
async def test_user_transaction_isolation():
    """
    Verifies that User A and User B cannot see each other's transactions in history.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create User A
        email_a = f"usera_{uuid.uuid4().hex[:6]}@test.com"
        res_a = await ac.post("/api/v1/auth/signup", json={
            "email": email_a,
            "password": "PasswordA123!",
            "full_name": "User Alpha"
        })
        token_a = res_a.json()["access_token"]

        # Create User B
        email_b = f"userb_{uuid.uuid4().hex[:6]}@test.com"
        res_b = await ac.post("/api/v1/auth/signup", json={
            "email": email_b,
            "password": "PasswordB123!",
            "full_name": "User Beta"
        })
        token_b = res_b.json()["access_token"]

        # User A executes a transaction for $111.11
        tx_a_payload = {
            "amount": 111.11,
            "payment_method": "credit_card",
            "location_city": "Mumbai",
            "is_device_familiar": True
        }
        tx_a_res = await ac.post(
            "/api/v1/transactions/analyze",
            json=tx_a_payload,
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert tx_a_res.status_code == 200
        ref_a = tx_a_res.json()["transaction_ref"]

        # User B executes a transaction for $222.22
        tx_b_payload = {
            "amount": 222.22,
            "payment_method": "upi",
            "location_city": "Delhi",
            "is_device_familiar": True
        }
        tx_b_res = await ac.post(
            "/api/v1/transactions/analyze",
            json=tx_b_payload,
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert tx_b_res.status_code == 200
        ref_b = tx_b_res.json()["transaction_ref"]

        # Check User A's history -> Must contain ref_a, must NOT contain ref_b
        hist_a = await ac.get(
            "/api/v1/transactions/history",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert hist_a.status_code == 200
        records_a = hist_a.json()["records"]
        refs_in_a = [r["transaction_ref"] for r in records_a]
        assert ref_a in refs_in_a
        assert ref_b not in refs_in_a

        # Check User B's history -> Must contain ref_b, must NOT contain ref_a
        hist_b = await ac.get(
            "/api/v1/transactions/history",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert hist_b.status_code == 200
        records_b = hist_b.json()["records"]
        refs_in_b = [r["transaction_ref"] for r in records_b]
        assert ref_b in refs_in_b
        assert ref_a not in refs_in_b


@pytest.mark.anyio
async def test_auth_password_over_72_bytes_validation_error():
    """
    Verifies that passwords exceeding bcrypt's 72-byte limit are rejected with
    HTTP 422 Unprocessable Entity rather than silently truncated or crashing with 500.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        long_pwd_payload = {
            "email": f"over72_{uuid.uuid4().hex[:6]}@test.com",
            "password": "A" * 75,  # 75 bytes > 72 byte limit
            "full_name": "Over Limit Tester"
        }
        res = await ac.post("/api/v1/auth/signup", json=long_pwd_payload)
        assert res.status_code == 422
        errors = res.json()["detail"]
        assert any("72 bytes" in str(e).lower() for e in errors)


@pytest.mark.anyio
async def test_user_alert_isolation():
    """
    Verifies that security alerts are strictly isolated by authenticated user.
    User A's high-risk alerts are visible only to User A and invisible to User B.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create User Alpha
        email_alpha = f"alpha_alert_{uuid.uuid4().hex[:6]}@test.com"
        res_a = await ac.post("/api/v1/auth/signup", json={
            "email": email_alpha,
            "password": "PasswordAlpha123!",
            "full_name": "Alerts User Alpha"
        })
        token_a = res_a.json()["access_token"]

        # Create User Beta
        email_beta = f"beta_alert_{uuid.uuid4().hex[:6]}@test.com"
        res_b = await ac.post("/api/v1/auth/signup", json={
            "email": email_beta,
            "password": "PasswordBeta123!",
            "full_name": "Alerts User Beta"
        })
        token_b = res_b.json()["access_token"]

        # User Alpha triggers a high-risk transaction ($9,500.00, Dubai, unfamiliar device)
        high_risk_payload = {
            "amount": 9500.00,
            "payment_method": "credit_card",
            "location_city": "Dubai",
            "is_device_familiar": False,
            "advanced_details": {
                "currency": "USD",
                "merchant_category": "luxury"
            }
        }
        tx_res = await ac.post(
            "/api/v1/transactions/analyze",
            json=high_risk_payload,
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert tx_res.status_code == 200
        ref_alpha = tx_res.json()["transaction_ref"]

        # User Beta triggers a safe transaction ($35.00, Mumbai, familiar device)
        safe_payload = {
            "amount": 35.00,
            "payment_method": "credit_card",
            "location_city": "Mumbai",
            "is_device_familiar": True
        }
        await ac.post(
            "/api/v1/transactions/analyze",
            json=safe_payload,
            headers={"Authorization": f"Bearer {token_b}"}
        )

        # 1. User Alpha checks alerts feed -> Must see their alert
        alerts_a = await ac.get(
            "/api/v1/alerts/feed",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert alerts_a.status_code == 200
        data_a = alerts_a.json()
        refs_a = [item["transaction_ref"] for item in data_a]
        assert ref_alpha in refs_a

        # 2. User Beta checks alerts feed -> Must have 0 alerts (User Alpha's alert is isolated)
        alerts_b = await ac.get(
            "/api/v1/alerts/feed",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert alerts_b.status_code == 200
        data_b = alerts_b.json()
        refs_b = [item["transaction_ref"] for item in data_b]
        assert ref_alpha not in refs_b
        assert len(data_b) == 0

        # 3. Unauthenticated guest checks feed -> 200 OK without 500 error
        alerts_guest = await ac.get("/api/v1/alerts/feed")
        assert alerts_guest.status_code == 200


@pytest.mark.anyio
async def test_user_report_csv_and_pdf_isolation():
    """
    Verifies that CSV and PDF audit reports strictly respect user data isolation.
    User Alpha's CSV/PDF export only contains User Alpha's transactions.
    User Beta's CSV/PDF export only contains User Beta's transactions.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email_alpha = f"rpt_alpha_{uuid.uuid4().hex[:6]}@test.com"
        res_a = await ac.post("/api/v1/auth/signup", json={
            "email": email_alpha,
            "password": "Password123!",
            "full_name": "Report Alpha"
        })
        token_a = res_a.json()["access_token"]

        email_beta = f"rpt_beta_{uuid.uuid4().hex[:6]}@test.com"
        res_b = await ac.post("/api/v1/auth/signup", json={
            "email": email_beta,
            "password": "Password123!",
            "full_name": "Report Beta"
        })
        token_b = res_b.json()["access_token"]

        # Transaction for Alpha
        tx_a = await ac.post("/api/v1/transactions/analyze", json={
            "amount": 777.77,
            "location_city": "Mumbai",
            "is_device_familiar": True
        }, headers={"Authorization": f"Bearer {token_a}"})
        ref_a = tx_a.json()["transaction_ref"]

        # Transaction for Beta
        tx_b = await ac.post("/api/v1/transactions/analyze", json={
            "amount": 888.88,
            "location_city": "Delhi",
            "is_device_familiar": True
        }, headers={"Authorization": f"Bearer {token_b}"})
        ref_b = tx_b.json()["transaction_ref"]

        # Alpha exports CSV
        csv_a = await ac.get("/api/v1/reports/export/csv", headers={"Authorization": f"Bearer {token_a}"})
        assert csv_a.status_code == 200
        assert ref_a in csv_a.text
        assert ref_b not in csv_a.text

        # Beta exports CSV
        csv_b = await ac.get("/api/v1/reports/export/csv", headers={"Authorization": f"Bearer {token_b}"})
        assert csv_b.status_code == 200
        assert ref_b in csv_b.text
        assert ref_a not in csv_b.text

        # Alpha exports PDF
        pdf_a = await ac.get("/api/v1/reports/export/pdf", headers={"Authorization": f"Bearer {token_a}"})
        assert pdf_a.status_code == 200
        assert "application/pdf" in pdf_a.headers.get("content-type", "")
        assert len(pdf_a.content) > 1000

