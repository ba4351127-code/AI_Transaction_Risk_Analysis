from typing import List, Dict, Any, Tuple
from backend.app.schemas.risk_result import (
    EverydayUserOutput,
    RiskAnalystOutput,
    ShapFeatureContribution,
    ModelDiagnostics
)
from backend.app.config import settings


# Mapping technical feature names to human-readable explanations
FEATURE_DISPLAY_NAMES = {
    "amount": "Transaction Amount",
    "amount_to_mean_ratio": "Amount vs Historical Average",
    "amount_zscore": "Spending Variance (Z-Score)",
    "is_device_familiar": "Device Familiarity",
    "geo_velocity_kmh": "Travel Speed (km/h)",
    "transaction_hour": "Time of Day",
    "payment_method_code": "Payment Method Risk",
    "location_risk_factor": "Geographic Location Risk",
    "anomaly_outlier_factor": "Pattern Outlier Index"
}


def translate_shap_contributions(
    shap_raw: List[Dict[str, Any]]
) -> List[ShapFeatureContribution]:
    """Formats raw SHAP outputs into structured attribution objects."""
    contributions: List[ShapFeatureContribution] = []

    for item in shap_raw:
        feature = item.get("feature", "unknown")
        val = item.get("value", 0)
        if hasattr(val, "item"):
            val = val.item()
        shap_val = float(item.get("shap_value", 0.0))
        
        display_name = FEATURE_DISPLAY_NAMES.get(feature, feature.replace("_", " ").title())
        direction = "increases_risk" if shap_val > 0 else "decreases_risk"
        
        abs_shap = abs(shap_val)
        if abs_shap > 0.25:
            magnitude = "Critical"
        elif abs_shap > 0.15:
            magnitude = "High"
        elif abs_shap > 0.05:
            magnitude = "Moderate"
        else:
            magnitude = "Low"

        contributions.append(ShapFeatureContribution(
            feature=feature,
            display_name=display_name,
            value=val,
            shap_value=round(shap_val, 4),
            direction=direction,
            impact_magnitude=magnitude
        ))

    return contributions


def generate_persona_explanations(
    overall_score: float,
    risk_category: str,
    recommended_action: str,
    model_signals: ModelDiagnostics,
    rules_triggered: List[str],
    rule_details: Dict[str, Any],
    top_shap: List[ShapFeatureContribution],
    behavioral_insights: List[str],
    amount: float,
    currency: str = "USD"
) -> Tuple[EverydayUserOutput, RiskAnalystOutput]:
    """
    Generates dual-persona outputs:
    1. Everyday User: plain-English headline, simple reasons, clear advice, color token.
    2. Risk Analyst: model signals, top SHAP features, rule triggers, technical synopsis.
    """
    # 1. Everyday User Persona
    simple_reasons: List[str] = []

    # Map color tokens based on risk category
    if risk_category == "LOW":
        badge_color = "#10B981"  # Emerald Green
        headline = "Safe Transaction"
        action_advice = "The transaction matches your regular spending pattern and is safe to approve."
        if not simple_reasons:
            simple_reasons.append("Amount is consistent with your typical spending habits.")
            simple_reasons.append("Initiated from a verified, familiar device.")
            simple_reasons.append("Location matches your common activity radius.")
            
    elif risk_category == "MEDIUM":
        badge_color = "#F59E0B"  # Amber
        headline = "Verification Recommended"
        action_advice = "We recommend secondary verification (OTP or biometric approval) before completing."
        
        # Add reasons based on rules and behavioral deviations
        for insight in behavioral_insights:
            simple_reasons.append(insight)
        if "UNFAMILIAR_DEVICE_ACCESS" in rules_triggered:
            simple_reasons.append("A new or unrecognized device was used.")
        if not simple_reasons:
            simple_reasons.append("Slight deviation detected from normal activity patterns.")

    elif risk_category == "HIGH":
        badge_color = "#EF4444"  # Red
        headline = "High Suspicious Activity"
        action_advice = "Decline this transaction immediately and confirm account ownership with the cardholder."
        
        for rule, detail in rule_details.items():
            if isinstance(detail, str):
                simple_reasons.append(detail)
        for insight in behavioral_insights[:2]:
            if insight not in simple_reasons:
                simple_reasons.append(insight)

    else:  # CRITICAL
        badge_color = "#7F1D1D"  # Deep Crimson
        headline = "Critical Threat Detected"
        action_advice = "Block this transaction immediately and initiate security freeze on the affected account."
        
        for rule, detail in rule_details.items():
            if isinstance(detail, str):
                simple_reasons.append(f"CRITICAL: {detail}")

    # Ensure everyday reasons are concise (2 to 4 items)
    if len(simple_reasons) > 4:
        simple_reasons = simple_reasons[:4]

    everyday_output = EverydayUserOutput(
        badge_color=badge_color,
        headline=headline,
        risk_category=risk_category,
        simple_reasons=simple_reasons,
        action_advice=action_advice
    )

    # 2. Risk Analyst Persona
    tech_summary = (
        f"Composite Score: {overall_score:.1f}/100 ({risk_category}). "
        f"ML P(Fraud)={model_signals.xgb_fraud_probability:.3f}, "
        f"IForest Outlier={model_signals.iforest_anomaly_score:.1f}/100, "
        f"Rule Penalty={model_signals.rule_penalty_score:.1f}, "
        f"Behavioral Z-Score={model_signals.behavioral_z_score:.2f}."
    )
    if rules_triggered:
        tech_summary += f" Triggered heuristics: {', '.join(rules_triggered)}."

    analyst_output = RiskAnalystOutput(
        model_signals=model_signals,
        top_shap_contributions=top_shap,
        rules_triggered=rules_triggered,
        technical_summary=tech_summary,
        feature_vector_snapshot={
            "amount": amount,
            "currency": currency,
            "rule_penalty": model_signals.rule_penalty_score,
            "xgb_prob": model_signals.xgb_fraud_probability,
            "iforest_score": model_signals.iforest_anomaly_score
        }
    )

    return everyday_output, analyst_output
