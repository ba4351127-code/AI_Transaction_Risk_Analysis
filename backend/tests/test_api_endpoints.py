import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database.session import init_db


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "TransactionGuard AI" in data["service"]


@pytest.mark.anyio
async def test_transaction_analyze_api_normal():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "amount": 75.0,
            "payment_method": "credit_card",
            "location_city": "Mumbai",
            "is_device_familiar": True
        }
        res = await ac.post("/api/v1/transactions/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "transaction_ref" in data
        assert 0.0 <= data["overall_risk_score"] <= 30.0
        assert data["risk_category"] == "LOW"
        assert data["recommended_action"] == "APPROVE"
        assert "everyday_user" in data
        assert "risk_analyst" in data
        assert len(data["everyday_user"]["simple_reasons"]) >= 1


@pytest.mark.anyio
async def test_transaction_analyze_api_high_risk():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "amount": 8500.0,
            "payment_method": "credit_card",
            "location_city": "London",
            "is_device_familiar": False,
            "advanced_details": {
                "user_identifier": "usr_9999",
                "currency": "USD",
                "merchant_category": "luxury_goods"
            }
        }
        res = await ac.post("/api/v1/transactions/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["overall_risk_score"] >= 70.0
        assert data["risk_category"] in ("HIGH", "CRITICAL")
        assert data["recommended_action"] == "BLOCK"
        assert len(data["risk_analyst"]["top_shap_contributions"]) >= 1


@pytest.mark.anyio
async def test_simulator_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "baseline_transaction": {
                "amount": 6000.0,
                "payment_method": "credit_card",
                "location_city": "Tokyo",
                "is_device_familiar": False
            },
            "modified_transaction": {
                "amount": 120.0,
                "payment_method": "credit_card",
                "location_city": "Tokyo",
                "is_device_familiar": True
            }
        }
        res = await ac.post("/api/v1/simulator/evaluate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "score_delta" in data
        assert data["score_delta"] < 0  # Reducing amount & familiar device reduces risk!
        assert "takeaway_summary" in data


@pytest.mark.anyio
async def test_model_metrics_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/intelligence/metrics")
        assert res.status_code == 200
        data = res.json()
        assert "roc_auc" in data
        assert "pr_auc" in data
        assert "confusion_matrix" in data


@pytest.mark.anyio
async def test_transaction_history_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/transactions/history?page=1&limit=10")
        assert res.status_code == 200
        data = res.json()
        assert "records" in data
        assert isinstance(data["records"], list)


@pytest.mark.anyio
async def test_alerts_feed_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/alerts/feed")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)


@pytest.mark.anyio
async def test_reports_export_csv_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/reports/export/csv")
        assert res.status_code == 200
        assert "text/csv" in res.headers.get("content-type", "")


@pytest.mark.anyio
async def test_global_features_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/intelligence/global-features")
        assert res.status_code == 200
        data = res.json()
        assert "features" in data
        assert len(data["features"]) == 17


@pytest.mark.anyio
async def test_transaction_analyze_invalid_inputs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Zero amount
        res_zero = await ac.post("/api/v1/transactions/analyze", json={"amount": 0.0})
        assert res_zero.status_code == 422

        # 2. Negative amount
        res_neg = await ac.post("/api/v1/transactions/analyze", json={"amount": -50.0})
        assert res_neg.status_code == 422

        # 3. Excessive amount over $100M limit
        res_huge = await ac.post("/api/v1/transactions/analyze", json={"amount": 150_000_000.0})
        assert res_huge.status_code == 422

        # 4. Invalid device familiarity type
        res_dev = await ac.post("/api/v1/transactions/analyze", json={"amount": 100.0, "is_device_familiar": "not_a_bool"})
        assert res_dev.status_code == 422


@pytest.mark.anyio
async def test_transaction_analyze_timestamp_formats():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # ISO string with UTC Z
        res_z = await ac.post("/api/v1/transactions/analyze", json={
            "amount": 90.0,
            "location_city": "Mumbai",
            "transaction_timestamp": "2026-11-22T08:00:00Z"
        })
        assert res_z.status_code == 200

        # ISO string with offset (+05:30)
        res_offset = await ac.post("/api/v1/transactions/analyze", json={
            "amount": 95.0,
            "location_city": "Mumbai",
            "transaction_timestamp": "2026-11-22T13:30:00+05:30"
        })
        assert res_offset.status_code == 200

        # ISO string naive (no offset)
        res_naive = await ac.post("/api/v1/transactions/analyze", json={
            "amount": 100.0,
            "location_city": "Mumbai",
            "transaction_timestamp": "2026-11-22T08:00:00"
        })
        assert res_naive.status_code == 200


@pytest.mark.anyio
async def test_transaction_analyze_consecutive_geo_velocity():
    """
    Verifies that consecutive transactions for the same authenticated user
    correctly compute geo velocity against SQLite historical timestamps
    without throwing TypeError: can't subtract offset-naive and offset-aware datetimes.
    """
    import uuid
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        user_email = f"geotest_{uuid.uuid4().hex[:6]}@test.com"
        signup_res = await ac.post("/api/v1/auth/signup", json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "Geo Velocity Tester"
        })
        assert signup_res.status_code in (200, 201)
        token = signup_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Tx 1: Mumbai
        tx1_res = await ac.post("/api/v1/transactions/analyze", json={
            "amount": 120.0,
            "payment_method": "credit_card",
            "location_city": "Mumbai",
            "is_device_familiar": True
        }, headers=headers)
        assert tx1_res.status_code == 200
        tx1_data = tx1_res.json()
        assert tx1_data["overall_risk_score"] <= 30.0

        # Tx 2: London moments later (impossible physical travel)
        tx2_res = await ac.post("/api/v1/transactions/analyze", json={
            "amount": 250.0,
            "payment_method": "credit_card",
            "location_city": "London",
            "is_device_familiar": True
        }, headers=headers)
        assert tx2_res.status_code == 200
        tx2_data = tx2_res.json()
        assert tx2_data["overall_risk_score"] >= 80.0
        assert tx2_data["risk_category"] in ("HIGH", "CRITICAL")
        assert tx2_data["recommended_action"] == "BLOCK"
