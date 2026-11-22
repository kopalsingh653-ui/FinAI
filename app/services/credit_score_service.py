import numpy as np

from app.schemas.credit_score import BorrowerFinancialDetails


PAY_COLUMNS = [
    "PAY_0", "PAY_2", "PAY_3",
    "PAY_4", "PAY_5", "PAY_6"
]


def calculate_repayment_score(credit):
    """
    Evaluates repayment history.
    PAY values <= 0 are treated as non-delinquent.
    Positive values represent delayed payments.
    """

    statuses = [
        getattr(credit, col)
        for col in PAY_COLUMNS
    ]

    penalties = []

    for status in statuses:
        if status <= 0:
            penalty = 0
        elif status == 1:
            penalty = 25
        elif status == 2:
            penalty = 50
        else:
            penalty = 75

        penalties.append(penalty)

    average_penalty = np.mean(penalties)

    return max(0, 100 - average_penalty)


def calculate_utilisation_score(credit):
    """
    Evaluates average outstanding balance
    relative to available credit.
    """

    credit_limit = credit.LIMIT_BAL

    if credit_limit <= 0:
        return 0, 0

    bills = [
        credit.BILL_AMT1,
        credit.BILL_AMT2,
        credit.BILL_AMT3,
        credit.BILL_AMT4,
        credit.BILL_AMT5,
        credit.BILL_AMT6
    ]

    average_bill = np.mean(bills)

    utilisation = max(0, average_bill / credit_limit)

    if utilisation <= 0.30:
        score = 100
    elif utilisation <= 0.50:
        score = 85
    elif utilisation <= 0.75:
        score = 65
    elif utilisation <= 1.00:
        score = 40
    else:
        score = 20

    return score, utilisation


def calculate_payment_behaviour_score(credit):
    """
    Evaluates payment consistency relative to
    outstanding bills.
    """

    bills = [
        credit.BILL_AMT1,
        credit.BILL_AMT2,
        credit.BILL_AMT3,
        credit.BILL_AMT4,
        credit.BILL_AMT5,
        credit.BILL_AMT6
    ]

    payments = [
        credit.PAY_AMT1,
        credit.PAY_AMT2,
        credit.PAY_AMT3,
        credit.PAY_AMT4,
        credit.PAY_AMT5,
        credit.PAY_AMT6
    ]

    total_bill = sum(abs(value) for value in bills)
    total_payment = sum(max(0, value) for value in payments)

    if total_bill == 0:
        return 75

    ratio = total_payment / total_bill

    if ratio >= 1:
        return 100
    elif ratio >= 0.75:
        return 85
    elif ratio >= 0.50:
        return 65
    elif ratio >= 0.25:
        return 45
    else:
        return 20


def calculate_affordability_score(financial):
    """
    Evaluates existing debt obligations
    relative to monthly income.

    Proposed loan EMI is assessed separately
    during loan eligibility evaluation.
    """

    income = financial.monthly_income

    existing_obligations = (
        financial.existing_emi
        + financial.other_monthly_debt
    )

    dti = existing_obligations / income

    if dti <= 0.20:
        score = 100
    elif dti <= 0.30:
        score = 85
    elif dti <= 0.40:
        score = 70
    elif dti <= 0.50:
        score = 45
    else:
        score = 20

    return score, dti


def get_score_band(score):

    if score >= 800:
        return "Excellent"
    elif score >= 750:
        return "Very Good"
    elif score >= 700:
        return "Good"
    elif score >= 650:
        return "Fair"
    elif score >= 550:
        return "Poor"
    else:
        return "Very Poor"


def calculate_credit_score(credit, financial):
    """
    Generates FinAI's internal credit score.

    Component weights:
    Repayment history: 40%
    Credit utilisation: 25%
    Payment behaviour: 20%
    Affordability: 15%
    """

    repayment_score = calculate_repayment_score(credit)

    utilisation_score, utilisation = (
        calculate_utilisation_score(credit)
    )

    payment_score = calculate_payment_behaviour_score(
        credit
    )

    affordability_score, dti = (
        calculate_affordability_score(financial)
    )

    weighted_score = (
        repayment_score * 0.40
        + utilisation_score * 0.25
        + payment_score * 0.20
        + affordability_score * 0.15
    )

    final_score = round(
        300 + (weighted_score / 100) * 600
    )

    strengths = []
    risk_factors = []

    if repayment_score >= 80:
        strengths.append("Good repayment history")
    elif repayment_score < 60:
        risk_factors.append("History of delayed payments")

    if utilisation < 0.30:
        strengths.append("Low credit utilisation")
    elif utilisation > 0.75:
        risk_factors.append("High credit utilisation")

    if payment_score >= 80:
        strengths.append("Consistent payment behaviour")
    elif payment_score < 50:
        risk_factors.append("Low payment-to-bill ratio")

    if dti <= 0.30:
        strengths.append("Manageable existing debt")
    elif dti > 0.40:
        risk_factors.append("High existing debt burden")

    return {
        "credit_score": final_score,
        "score_band": get_score_band(final_score),

        "repayment_history_score": round(
            repayment_score, 2
        ),

        "utilisation_score": round(
            utilisation_score, 2
        ),

        "payment_behaviour_score": round(
            payment_score, 2
        ),

        "affordability_score": round(
            affordability_score, 2
        ),

        "debt_to_income_ratio": round(dti, 4),

        "credit_utilisation": round(
            utilisation, 4
        ),

        "strengths": strengths,
        "risk_factors": risk_factors,

        "methodology": (
            "Internal rule-based FinAI score using "
            "repayment history, credit utilisation, "
            "payment behaviour and affordability."
        )
    }