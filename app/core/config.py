from pathlib import Path
from pydantic_settings import BaseSettings


# Project root directory
ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    APP_NAME: str = "FinAI"
    APP_VERSION: str = "1.0.0"

    APP_DESCRIPTION: str = (
        "AI-powered Financial Inclusion and "
        "Responsible Lending Platform"
    )

    DEBUG: bool = True

    # Model paths
    MODEL_PATH: Path = (
        ROOT_DIR / "models" / "best_credit_model.joblib"
    )

    METADATA_PATH: Path = (
        ROOT_DIR / "models" / "model_metadata.json"
    )

    THRESHOLD_PATH: Path = (
        ROOT_DIR / "results" / "metrics" / "selected_threshold.json"
    )

    # Database
    DATABASE_PATH: Path = (
        ROOT_DIR / "finai.db"
    )

    DATABASE_URL: str = (
        f"sqlite:///{DATABASE_PATH.as_posix()}"
    )

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8501"
    ]

    model_config = {
    "env_file": ".env",
    "extra": "ignore"
    }


settings = Settings()