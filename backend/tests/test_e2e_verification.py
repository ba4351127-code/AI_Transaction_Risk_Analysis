import asyncio, uuid, sqlite3
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.anyio
async def test_complete_e2e_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        # 1. USER ALPHA REGISTRATION & LOGIN
        email_a = f'alpha_e2e_{uuid.uuid4().hex[:6]}@test.com'
        pwd_a = 'AlphaPass123!'
        res_signup_a = await ac.post('/api/v1/auth/signup', json={
            'email': email_a,
            'password': pwd_a,
            'full_name': 'Alpha Tester'
        })
        assert res_signup_a.status_code == 201
        token_a = res_signup_a.json()['access_token']
        headers_a = {'Authorization': f'Bearer {token_a}'}

        # Profile check
        me_a = await ac.get('/api/v1/auth/me', headers=headers_a)
        assert me_a.status_code == 200
        assert me_a.json()['email'] == email_a

        # 2. ALPHA SUBMITS TRANSACTIONS
        # Tx 1: Low risk ($50 Mumbai, familiar device)
        tx1 = await ac.post('/api/v1/transactions/analyze', json={
            'amount': 50.0,
            'payment_method': 'credit_card',
            'location_city': 'Mumbai',
            'is_device_familiar': True
        }, headers=headers_a)
        assert tx1.status_code == 200
        data1 = tx1.json()
        ref_a1 = data1['transaction_ref']
        assert data1['risk_category'] == 'LOW'
        assert data1['recommended_action'] == 'APPROVE'

        # Tx 2: High risk ($8500 Tokyo, unfamiliar device)
        tx2 = await ac.post('/api/v1/transactions/analyze', json={
            'amount': 8500.0,
            'payment_method': 'wire_transfer',
            'location_city': 'Tokyo',
            'is_device_familiar': False,
            'advanced_details': {
                'merchant_category': 'luxury_goods'
            }
        }, headers=headers_a)
        assert tx2.status_code == 200
        data2 = tx2.json()
        ref_a2 = data2['transaction_ref']
        assert data2['risk_category'] in ('HIGH', 'CRITICAL')
        assert data2['recommended_action'] == 'BLOCK'

        # 3. VERIFY ALPHA HISTORY & ALERTS
        hist_a = await ac.get('/api/v1/transactions/history', headers=headers_a)
        assert hist_a.status_code == 200
        a_records = hist_a.json()['records']
        a_refs = [r['transaction_ref'] for r in a_records]
        assert ref_a1 in a_refs and ref_a2 in a_refs

        alerts_a = await ac.get('/api/v1/alerts/feed', headers=headers_a)
        assert alerts_a.status_code == 200
        a_alerts = alerts_a.json()
        assert any(item['transaction_ref'] == ref_a2 for item in a_alerts)

        # Alpha CSV Export
        csv_a = await ac.get('/api/v1/reports/export/csv', headers=headers_a)
        assert csv_a.status_code == 200
        assert ref_a1 in csv_a.text and ref_a2 in csv_a.text

        # 4. USER BETA REGISTRATION & ISOLATION CHECK
        email_b = f'beta_e2e_{uuid.uuid4().hex[:6]}@test.com'
        pwd_b = 'BetaPass123!'
        res_signup_b = await ac.post('/api/v1/auth/signup', json={
            'email': email_b,
            'password': pwd_b,
            'full_name': 'Beta Tester'
        })
        assert res_signup_b.status_code == 201
        token_b = res_signup_b.json()['access_token']
        headers_b = {'Authorization': f'Bearer {token_b}'}

        # Beta History Check -> Must NOT see Alpha records
        hist_b = await ac.get('/api/v1/transactions/history', headers=headers_b)
        assert hist_b.status_code == 200
        b_records = hist_b.json()['records']
        b_refs = [r['transaction_ref'] for r in b_records]
        assert ref_a1 not in b_refs and ref_a2 not in b_refs
        assert len(b_records) == 0

        # Beta Alerts Check -> Must NOT see Alpha alerts
        alerts_b = await ac.get('/api/v1/alerts/feed', headers=headers_b)
        assert alerts_b.status_code == 200
        b_alerts = alerts_b.json()
        assert len(b_alerts) == 0

        # Beta attempts to download Alpha PDF report -> Must return 404
        pdf_b_leak_attempt = await ac.get(f'/api/v1/reports/export/pdf/{ref_a1}', headers=headers_b)
        assert pdf_b_leak_attempt.status_code == 404

        # Beta submits a Medium risk transaction ($750 unfamiliar device)
        tx_b1 = await ac.post('/api/v1/transactions/analyze', json={
            'amount': 750.0,
            'payment_method': 'credit_card',
            'location_city': 'Mumbai',
            'is_device_familiar': False
        }, headers=headers_b)
        assert tx_b1.status_code == 200
        data_b1 = tx_b1.json()
        ref_b1 = data_b1['transaction_ref']
        assert data_b1['risk_category'] == 'MEDIUM'
        assert data_b1['recommended_action'] == 'REVIEW'

        # Beta history now contains Beta ref, still zero Alpha refs
        hist_b2 = await ac.get('/api/v1/transactions/history', headers=headers_b)
        b2_refs = [r['transaction_ref'] for r in hist_b2.json()['records']]
        assert ref_b1 in b2_refs and ref_a1 not in b2_refs and ref_a2 not in b2_refs

        # 5. SESSION PERSISTENCE & RELOGIN
        login_a = await ac.post('/api/v1/auth/login', json={'email': email_a, 'password': pwd_a})
        assert login_a.status_code == 200
        token_a_new = login_a.json()['access_token']
        headers_a_new = {'Authorization': f'Bearer {token_a_new}'}

        # Alpha data is still intact
        hist_a_relogin = await ac.get('/api/v1/transactions/history', headers=headers_a_new)
        relogin_refs = [r['transaction_ref'] for r in hist_a_relogin.json()['records']]
        assert ref_a1 in relogin_refs and ref_a2 in relogin_refs

        # 6. DATABASE LEDGER PERSISTENCE CHECK
        conn = sqlite3.connect('backend/transactionguard.db')
        cur = conn.cursor()
        cur.execute('SELECT count(*) FROM users')
        u_count = cur.fetchone()[0]
        cur.execute('SELECT count(*) FROM transactions')
        t_count = cur.fetchone()[0]
        cur.execute('SELECT count(*) FROM alerts')
        a_count = cur.fetchone()[0]
        assert u_count >= 2
        assert t_count >= 3
