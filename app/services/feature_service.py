import numpy as np
import pandas as pd

from src.feature_engineering import add_financial_features


def build_model_features(credit_data, feature_names):
    """
    Convert raw borrower credit information into the exact
    feature structure expected by the trained FinAI model.

    Uses the same feature-engineering function as model training.
    """

    # Convert input into a single-row DataFrame.
    df = pd.DataFrame([credit_data])

    # Generate engineered financial features.
    df = add_financial_features(df)

    # Check that every trained model feature exists.
    missing_features = [
        feature
        for feature in feature_names
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            "Generated features missing: "
            + ", ".join(missing_features)
        )

    # Maintain the exact feature order used during training.
    X = df[feature_names].copy()

    # Convert all features to numeric.
    for column in X.columns:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    # Handle numerical instability.
    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # The trained model pipeline should contain an imputer.
    # Confirm that missing values can be handled.
    if X.isna().all(axis=1).iloc[0]:
        raise ValueError(
            "All model features are missing or invalid."
        )

    return X