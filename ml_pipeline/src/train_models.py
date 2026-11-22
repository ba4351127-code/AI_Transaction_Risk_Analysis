import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix
)
from xgboost import XGBClassifier
import shap
import joblib

# Set paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "synthetic"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def build_feature_matrix(df: pd.DataFrame):
    """Engineers numeric and cyclic features from raw transaction records."""
    df_feat = df.copy()
    
    # 1. Financial features
    df_feat["amount_log"] = np.log1p(df_feat["amount"].astype(float))
    if "amount_to_user_avg" not in df_feat.columns:
        df_feat["amount_to_user_avg"] = df_feat["amount"] / 350.0

    # 2. Cyclic temporal features
    hours = df_feat["transaction_hour"].astype(float)
    df_feat["hour_sin"] = np.sin(2 * np.pi * hours / 24.0)
    df_feat["hour_cos"] = np.cos(2 * np.pi * hours / 24.0)
    
    # 3. Familiarity
    df_feat["is_device_familiar"] = df_feat["is_device_familiar"].astype(int)

    feature_cols = [
        "amount",
        "amount_log",
        "amount_to_user_avg",
        "hour_sin",
        "hour_cos",
        "is_device_familiar",
        "payment_method",
        "merchant_category"
    ]
    
    return df_feat[feature_cols]


def train_and_export():
    from ml_pipeline.src.synthetic_generator import generate_synthetic_transactions
    
    print("[1/5] Generating dataset...")
    df = generate_synthetic_transactions(num_records=6000, fraud_ratio=0.04)
    y = df["is_fraud"].values
    
    X_raw = build_feature_matrix(df)
    
    # Stratified Train/Test split
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y, test_size=0.20, random_state=42, stratify=y
    )
    
    print(f"Dataset split: Train={len(X_train_raw)} (Fraud={y_train.sum()}), Test={len(X_test_raw)} (Fraud={y_test.sum()})")
    
    # Numerical & Categorical preprocessors
    num_cols = ["amount", "amount_log", "amount_to_user_avg", "hour_sin", "hour_cos", "is_device_familiar"]
    cat_cols = ["payment_method", "merchant_category"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", RobustScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
        ]
    )
    
    print("[2/5] Fitting preprocessor pipeline...")
    X_train = preprocessor.fit_transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)
    
    # Extract feature names after one-hot encoding
    cat_feature_names = list(preprocessor.named_transformers_["cat"].get_feature_names_out(cat_cols))
    all_feature_names = num_cols + cat_feature_names
    
    # 3. Supervised Model: XGBoost
    print("[3/5] Training Supervised XGBoost Classifier...")
    pos_weight = (len(y_train) - y_train.sum()) / max(y_train.sum(), 1)
    
    xgb_model = XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=pos_weight,
        eval_metric="logloss",
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    
    # Evaluate XGBoost
    y_pred_proba = xgb_model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.50).astype(int)
    
    roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    pr_auc = float(average_precision_score(y_test, y_pred_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print(f"XGBoost Test Performance: ROC-AUC = {roc_auc:.4f}, PR-AUC = {pr_auc:.4f}")
    
    # 4. Unsupervised Model: Isolation Forest
    print("[4/5] Training Unsupervised Isolation Forest...")
    # Train primarily on normal instances
    X_train_normal = X_train[y_train == 0]
    
    iforest = IsolationForest(
        n_estimators=100,
        contamination=0.04,
        random_state=42,
        n_jobs=-1
    )
    iforest.fit(X_train_normal)
    
    # 5. Explainability Pipeline: SHAP TreeExplainer
    print("[5/5] Building SHAP TreeExplainer...")
    # Use 100 background samples as numpy array
    background_data = X_train[:100]
    explainer = shap.TreeExplainer(xgb_model, data=background_data)
    
    # Save artifacts
    print("Saving serialized model artifacts to:", MODELS_DIR)
    joblib.dump(preprocessor, MODELS_DIR / "preprocessor.joblib")
    joblib.dump(xgb_model, MODELS_DIR / "xgboost_model.joblib")
    joblib.dump(iforest, MODELS_DIR / "isolation_forest.joblib")
    joblib.dump(explainer, MODELS_DIR / "shap_summary.joblib")
    joblib.dump(all_feature_names, MODELS_DIR / "feature_names.joblib")
    
    metrics = {
        "dataset_size": len(df),
        "test_size": len(X_test),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": cm,
        "feature_count": len(all_feature_names),
        "top_features": all_feature_names[:6]
    }
    
    with open(BASE_DIR / "evaluation_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("Training complete! Model artifacts successfully generated.")
    return metrics


if __name__ == "__main__":
    train_and_export()
