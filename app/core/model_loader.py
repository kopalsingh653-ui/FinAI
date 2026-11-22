import json
import joblib

from pathlib import Path
from functools import lru_cache

from app.core.config import settings


class FinAIModel:

    def __init__(self):

        self.model = None
        self.metadata = {}
        self.feature_names = []
        self.threshold = 0.50

        self.load()

    def load(self):

        if not settings.MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found: {settings.MODEL_PATH}"
            )

        if not settings.METADATA_PATH.exists():
            raise FileNotFoundError(
                f"Metadata not found: {settings.METADATA_PATH}"
            )

        print("Loading FinAI credit risk model...")

        self.model = joblib.load(
            settings.MODEL_PATH
        )

        with open(
            settings.METADATA_PATH,
            "r"
        ) as file:
            self.metadata = json.load(file)

        self.feature_names = (
            self.metadata.get("feature_names")
            or self.metadata.get("features")
            or list(getattr(self.model, "feature_names_in_", []))
        )

        if not self.feature_names:
            raise ValueError(
                "Model feature names could not be loaded."
            )

        if settings.THRESHOLD_PATH.exists():

            with open(
                settings.THRESHOLD_PATH,
                "r"
            ) as file:

                threshold_data = json.load(file)

                self.threshold = float(
                    threshold_data.get(
                        "selected_threshold",
                        0.50
                    )
                )

        print("FinAI model loaded successfully.")
        print("Number of features:", len(self.feature_names))
        print("Prediction threshold:", self.threshold)

    def predict_probability(self, features):

        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        probabilities = self.model.predict_proba(
            features
        )

        return probabilities[:, 1]

    def predict_class(self, probabilities):

        return (
            probabilities >= self.threshold
        ).astype(int)


@lru_cache(maxsize=1)
def get_model():

    return FinAIModel()