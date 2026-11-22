from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ShapFeatureContribution(BaseModel):
    feature: str = Field(..., description="Feature variable name")
    display_name: str = Field(..., description="Human-friendly label e.g., 'Transaction Amount vs Normal'")
    value: Any = Field(..., description="Current transaction feature value")
    shap_value: float = Field(..., description="Exact Shapley contribution score")
    direction: str = Field(..., description="'increases_risk' or 'decreases_risk'")
    impact_magnitude: str = Field(..., description="'Critical', 'High', 'Moderate', 'Low'")


class ModelDiagnostics(BaseModel):
    xgb_fraud_probability: float = Field(..., ge=0.0, le=1.0)
    iforest_anomaly_score: float = Field(..., description="Normalized anomaly metric 0.0 - 100.0")
    rule_penalty_score: float = Field(..., ge=0.0, le=100.0)
    behavioral_deviation_score: float = Field(..., ge=0.0, le=100.0)
    behavioral_z_score: float = Field(default=0.0, description="Statistical Z-Score vs personal mean")
    confidence_score: float = Field(default=95.0, ge=0.0, le=100.0)


class EverydayUserOutput(BaseModel):
    badge_color: str = Field(..., description="Hex color token (#10B981, #F59E0B, #EF4444, #7F1D1D)")
    headline: str = Field(..., description="Clear title e.g., 'Low Risk - Transaction Safe'")
    risk_category: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    simple_reasons: List[str] = Field(..., description="2-4 plain-English bullet explanations")
    action_advice: str = Field(..., description="Clear actionable next step for the everyday user")


class RiskAnalystOutput(BaseModel):
    model_signals: ModelDiagnostics
    top_shap_contributions: List[ShapFeatureContribution]
    rules_triggered: List[str]
    technical_summary: str
    feature_vector_snapshot: Dict[str, Any]


class RiskAssessmentResponse(BaseModel):
    transaction_ref: str
    user_identifier: Optional[str] = None
    overall_risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_category: str
    recommended_action: str  # APPROVE, REVIEW, BLOCK
    
    everyday_user: EverydayUserOutput
    risk_analyst: RiskAnalystOutput
    
    evaluated_at: datetime
