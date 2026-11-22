from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

# Resolve base directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = BACKEND_DIR.parent
ML_MODELS_DIR = BASE_DIR / "ml_pipeline" / "models"
REPORTS_DIR = BACKEND_DIR / "generated_reports"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "TransactionGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # JWT Authentication & Security
    JWT_SECRET_KEY: str = "transactionguard_super_secret_jwt_key_2026_fintech_secure"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Database Configuration: Defaults to local aiosqlite, seamless switch to PostgreSQL
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BACKEND_DIR.as_posix()}/transactionguard.db"
    
    # ML Model Artifacts
    MODEL_DIR: str = str(ML_MODELS_DIR)
    XGB_MODEL_PATH: str = str(ML_MODELS_DIR / "xgboost_model.joblib")
    IFOREST_MODEL_PATH: str = str(ML_MODELS_DIR / "isolation_forest.joblib")
    PREPROCESSOR_PATH: str = str(ML_MODELS_DIR / "preprocessor.joblib")
    SHAP_SUMMARY_PATH: str = str(ML_MODELS_DIR / "shap_summary.joblib")
    
    # Risk Scoring Weights
    WEIGHT_RULE: float = 0.20
    WEIGHT_XGB: float = 0.45
    WEIGHT_IFOREST: float = 0.20
    WEIGHT_BEHAVIORAL: float = 0.15
    
    # Risk Thresholds
    THRESHOLD_LOW: float = 30.0
    THRESHOLD_MEDIUM: float = 70.0
    THRESHOLD_HIGH: float = 89.0
    # > 89.0 is CRITICAL
    
    # Velocity threshold (km/h) for geo-teleportation checks
    MAX_PLAUSIBLE_VELOCITY_KMH: float = 900.0


settings = Settings()
