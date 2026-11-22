from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth,
    transactions,
    bulk,
    simulator,
    alerts,
    intelligence,
    reports
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(bulk.router, prefix="/bulk", tags=["Bulk Processing"])
api_router.include_router(simulator.router, prefix="/simulator", tags=["What-If Simulator"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Risk Intelligence"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
