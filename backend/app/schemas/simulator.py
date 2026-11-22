from pydantic import BaseModel, Field
from typing import Optional
from backend.app.schemas.transaction import TransactionAnalyzeRequest
from backend.app.schemas.risk_result import RiskAssessmentResponse


class SimulatorScenarioRequest(BaseModel):
    baseline_transaction: TransactionAnalyzeRequest
    modified_transaction: TransactionAnalyzeRequest
    scenario_notes: Optional[str] = Field(default=None, description="Optional note describing the what-if experiment")


class SimulatorComparisonResponse(BaseModel):
    baseline: RiskAssessmentResponse
    modified: RiskAssessmentResponse
    score_delta: float = Field(..., description="modified.score - baseline.score")
    category_changed: bool
    action_changed: bool
    primary_influencing_change: str
    takeaway_summary: str
