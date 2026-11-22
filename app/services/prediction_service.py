from app.core.model_loader import get_model
from app.services.feature_service import build_model_features


# Illustrative LGD assumption.
DEFAULT_LGD = 0.45


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def get_risk_category(probability):

    if probability < 0.10:
        return "Low Risk"

    elif probability < 0.25:
        return "Moderate Risk"

    elif probability < 0.50:
        return "High Risk"

    return "Very High Risk"


# ============================================================
# CREDIT RISK PREDICTION
# ============================================================

def generate_prediction(
    credit_features,
    requested_loan_amount
):

    model_loader = get_model()

    # Generate the exact model input.
    X = build_model_features(
        credit_data=credit_features,
        feature_names=model_loader.feature_names
    )

    # Generate default probability.
    probability = float(
        model_loader.predict_probability(X)[0]
    )

    # Apply the validation-selected threshold.
    predicted_class = int(
        probability >= model_loader.threshold
    )

    # Classify risk.
    risk_category = get_risk_category(probability)

    # Illustrative expected loss calculation.
    ead = float(requested_loan_amount)

    expected_loss = (
        probability * DEFAULT_LGD * ead
    )

    return {
        "default_probability": probability,
        "predicted_class": predicted_class,
        "risk_category": risk_category,
        "threshold": float(model_loader.threshold),
        "expected_loss": float(expected_loss),
        "lgd_assumption": DEFAULT_LGD,
        "ead_assumption": ead
    }