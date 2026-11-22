from app.core.model_loader import get_model
from app.services.feature_service import build_model_features
from app.services.credit_score_service import calculate_credit_score


# Illustrative project decision thresholds.
MIN_CREDIT_SCORE = 650
MAX_ACCEPTABLE_PD = 0.25
MAX_DTI = 0.40
MAX_PROPOSED_EMI_RATIO = 0.30
MIN_DISPOSABLE_INCOME = 5000

# Illustrative assumptions, not calibrated lending parameters.
LGD_ASSUMPTION = 0.45


def calculate_eligibility(request):

    credit = request.credit_features
    financial = request.financial_details

    # 1. Internal FinAI credit score.
    credit_result = calculate_credit_score(
        credit,
        financial
    )

    # 2. XGBoost default probability.
    model = get_model()

    model_features = build_model_features(
        credit.model_dump(),
        model.feature_names
    )

    probability = float(
        model.predict_probability(model_features)[0]
    )

    probability = max(0.0, min(1.0, probability))

    predicted_class = int(
    probability >= model.threshold
    )

    # 3. Affordability.
    income = financial.monthly_income
    expenses = financial.monthly_expenses

    existing_obligations = (
        financial.existing_emi
        + financial.other_monthly_debt
    )

    total_obligations = (
        existing_obligations
        + request.proposed_emi
    )

    dti = existing_obligations / income

    proposed_emi_ratio = (
        request.proposed_emi / income
    )

    disposable_income = (
        income
        - expenses
        - total_obligations
    )

    # 4. Illustrative expected loss.
    expected_loss = (
        probability
        * LGD_ASSUMPTION
        * request.requested_loan_amount
    )

    # 5. Risk classification.
    if probability < 0.10:
        risk_category = "Low"
    elif probability < 0.25:
        risk_category = "Moderate"
    elif probability < 0.50:
        risk_category = "High"
    else:
        risk_category = "Very High"

    # 6. Eligibility assessment.
    reasons = []
    recommendations = []
    hard_failures = []

    if credit_result["credit_score"] < MIN_CREDIT_SCORE:
        hard_failures.append(
            "Credit score is below the configured minimum."
        )

    if probability > MAX_ACCEPTABLE_PD:
        hard_failures.append(
            "Predicted default probability exceeds the configured limit."
        )

    if dti > MAX_DTI:
        hard_failures.append(
            "Existing debt-to-income ratio is too high."
        )

    if proposed_emi_ratio > MAX_PROPOSED_EMI_RATIO:
        hard_failures.append(
            "Proposed EMI exceeds the configured income limit."
        )

    if disposable_income < MIN_DISPOSABLE_INCOME:
        hard_failures.append(
            "Disposable monthly income is below the configured minimum."
        )

    if hard_failures:
        status = "Not Currently Eligible"
        reasons.extend(hard_failures)

    else:
        caution_factors = []

        if credit_result["credit_score"] < 700:
            caution_factors.append(
                "Credit score indicates a moderate credit profile."
            )

        if probability > 0.15:
            caution_factors.append(
                "Default probability requires additional review."
            )

        if dti > 0.30:
            caution_factors.append(
                "Existing debt burden is relatively high."
            )

        if proposed_emi_ratio > 0.25:
            caution_factors.append(
                "Proposed EMI uses a relatively high share of income."
            )

        if caution_factors:
            status = "Conditionally Eligible"
            reasons.extend(caution_factors)

            recommendations.append(
                "Review income documents and existing loan obligations."
            )

        else:
            status = "Eligible"

            reasons.append(
                "Applicant meets the configured FinAI assessment criteria."
            )

    # 7. Recommendations.
    if credit_result["credit_utilisation"] > 0.75:
        recommendations.append(
            "Consider reducing outstanding credit balances."
        )

    if credit_result["debt_to_income_ratio"] > 0.30:
        recommendations.append(
            "Consider reducing existing monthly debt obligations."
        )

    if probability > 0.15:
        recommendations.append(
            "Review repayment history and verify supporting documents."
        )

    if not recommendations:
        recommendations.append(
            "Continue with standard document verification."
        )

    # 8. Public assessment response.
    result = {
        "credit_score": credit_result["credit_score"],
        "score_band": credit_result["score_band"],
        "default_probability": round(probability, 4),
        "risk_category": risk_category,
        "debt_to_income_ratio": round(dti, 4),
        "proposed_emi_ratio": round(proposed_emi_ratio, 4),
        "disposable_income": round(disposable_income, 2),
        "expected_loss": round(expected_loss, 2),
        "eligibility_status": status,
        "eligibility_reason": reasons,
        "recommendations": recommendations,
        "disclaimer": (
            "This is an illustrative FinAI decision-support assessment. "
            "It is not an official credit bureau score, bank approval, "
            "or regulated lending decision."
        )
    }

    # Internal details used by the API to persist component scores.
    result["_credit_score_details"] = credit_result
    result["_predicted_class"] = predicted_class
    result["_model_threshold"] = model.threshold

    return result