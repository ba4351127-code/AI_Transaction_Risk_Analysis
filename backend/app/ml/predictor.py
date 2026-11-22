import os
import threading
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from pathlib import Path
from backend.app.config import settings

# Global cache and lock for thread-safe model artifact loading
_MODEL_CACHE: Dict[str, Any] = {}
_LOAD_LOCK = threading.Lock()
_REQUIRED_KEYS = {"preprocessor", "xgb_model", "iforest", "shap_explainer", "feature_names"}


def load_model_artifacts() -> Dict[str, Any]:
    """Loads serialized ML pipeline artifacts into memory with thread safety."""
    if _REQUIRED_KEYS.issubset(_MODEL_CACHE.keys()):
        return _MODEL_CACHE

    with _LOAD_LOCK:
        if _REQUIRED_KEYS.issubset(_MODEL_CACHE.keys()):
            return _MODEL_CACHE

        models_dir = Path(settings.MODEL_DIR)
        preprocessor_path = models_dir / "preprocessor.joblib"
        xgb_path = models_dir / "xgboost_model.joblib"
        iforest_path = models_dir / "isolation_forest.joblib"
        shap_path = models_dir / "shap_summary.joblib"
        feature_names_path = models_dir / "feature_names.joblib"

        if not xgb_path.exists():
            raise FileNotFoundError(
                f"Model artifacts not found at {models_dir}. "
                "Please run 'python -m ml_pipeline.src.train_models' first."
            )

        # Load all artifacts atomically before exposing to cache
        loaded = {
            "preprocessor": joblib.load(preprocessor_path),
            "xgb_model": joblib.load(xgb_path),
            "iforest": joblib.load(iforest_path),
            "shap_explainer": joblib.load(shap_path),
            "feature_names": joblib.load(feature_names_path)
        }
        _MODEL_CACHE.update(loaded)
        return _MODEL_CACHE


def transform_single_transaction(
    amount: float,
    payment_method: str,
    merchant_category: str,
    is_device_familiar: bool,
    hour: int,
    user_avg_amount: float = 350.0
) -> pd.DataFrame:
    """Prepares raw single-row DataFrame matching the model's feature space."""
    amount_log = np.log1p(float(amount))
    amount_to_user_avg = float(amount) / max(user_avg_amount, 1.0)
    hour_sin = np.sin(2 * np.pi * float(hour) / 24.0)
    hour_cos = np.cos(2 * np.pi * float(hour) / 24.0)

    data = {
        "amount": [float(amount)],
        "amount_log": [amount_log],
        "amount_to_user_avg": [amount_to_user_avg],
        "hour_sin": [hour_sin],
        "hour_cos": [hour_cos],
        "is_device_familiar": [1 if is_device_familiar else 0],
        "payment_method": [payment_method],
        "merchant_category": [merchant_category]
    }
    return pd.DataFrame(data)


def predict_transaction_risk(
    amount: float,
    payment_method: str = "credit_card",
    merchant_category: str = "general",
    is_device_familiar: bool = True,
    hour: int = 12,
    user_avg_amount: float = 350.0
) -> Tuple[float, float, List[Dict[str, Any]]]:
    """
    Executes real ML inference:
    1. Transforms features using ColumnTransformer
    2. Runs XGBoost predict_proba -> P(Fraud)
    3. Runs Isolation Forest decision_function -> Anomaly Score (0 - 100)
    4. Computes SHAP Shapley values -> Top 5 contributors
    
    Returns (xgb_fraud_prob, iforest_score, top_shap_list).
    """
    artifacts = load_model_artifacts()
    preprocessor = artifacts["preprocessor"]
    xgb_model = artifacts["xgb_model"]
    iforest = artifacts["iforest"]
    explainer = artifacts["shap_explainer"]
    feature_names = artifacts["feature_names"]

    # 1. Transform input
    df_raw = transform_single_transaction(
        amount=amount,
        payment_method=payment_method,
        merchant_category=merchant_category,
        is_device_familiar=is_device_familiar,
        hour=hour,
        user_avg_amount=user_avg_amount
    )
    X_transformed = preprocessor.transform(df_raw)

    # 2. Supervised XGBoost Probability
    xgb_proba = float(xgb_model.predict_proba(X_transformed)[0, 1])

    # 3. Unsupervised Isolation Forest Score
    # Raw decision_function returns negative for outliers, positive for inliers
    raw_score = float(iforest.decision_function(X_transformed)[0])
    # Normalize: raw score typically ranges from -0.3 to +0.2
    # Map to 0 (inlier) to 100 (extreme outlier)
    normalized_iforest = max(0.0, min(100.0, (0.20 - raw_score) * 200.0))

    # 4. SHAP Values
    shap_raw = explainer.shap_values(X_transformed)
    if isinstance(shap_raw, list):
        # In binary classification, some versions return [class_0, class_1]
        vals = shap_raw[1][0] if len(shap_raw) > 1 else shap_raw[0][0]
    elif hasattr(shap_raw, "ndim") and shap_raw.ndim == 2:
        vals = shap_raw[0]
    elif hasattr(shap_raw, "values"):
        vals = shap_raw.values[0]
        if hasattr(vals, "ndim") and vals.ndim > 1:
            vals = vals[:, 1]
    else:
        vals = np.zeros(len(feature_names))

    # Pair features with their SHAP contribution
    shap_contributions = []
    for feat_name, shap_v in zip(feature_names, vals):
        clean_name = feat_name.replace("num__", "").replace("cat__", "")
        val = df_raw.get(clean_name, [0])[0] if clean_name in df_raw.columns else 1
        if hasattr(val, "item"):
            val = val.item()
        shap_contributions.append({
            "feature": clean_name,
            "value": val,
            "shap_value": float(shap_v)
        })

    # Sort by absolute SHAP impact descending
    shap_contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    top_5_shap = shap_contributions[:5]

    return round(xgb_proba, 4), round(normalized_iforest, 2), top_5_shap
