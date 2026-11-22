import json
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = ROOT / "results" / "reports"
METRICS_DIR = ROOT / "results" / "metrics"

# Illustrative affordability thresholds.
# These are configurable project assumptions, not universal
# lending or regulatory requirements.

MAX_DTI = 0.40
MAX_EMI_TO_INCOME = 0.30
MIN_DISPOSABLE_INCOME = 5000


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_borrower_input(
    monthly_income,
    monthly_expenses,
    existing_emi,
    proposed_emi,
    other_monthly_debt=0
):

    values = {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "existing_emi": existing_emi,
        "proposed_emi": proposed_emi,
        "other_monthly_debt": other_monthly_debt
    }

    for name, value in values.items():

        if not isinstance(value, (int, float)):
            raise ValueError(
                f"{name} must be a numeric value."
            )

        if not np.isfinite(value) or value < 0:
            raise ValueError(
                f"{name} must be a finite, non-negative value."
            )

    if monthly_income <= 0:
        raise ValueError(
            "Monthly income must be greater than zero."
        )


# ============================================================
# AFFORDABILITY CALCULATION
# ============================================================

def calculate_affordability(
    monthly_income,
    monthly_expenses,
    existing_emi,
    proposed_emi,
    other_monthly_debt=0
):

    validate_borrower_input(
        monthly_income,
        monthly_expenses,
        existing_emi,
        proposed_emi,
        other_monthly_debt
    )

    total_existing_debt = (
        existing_emi + other_monthly_debt
    )

    total_monthly_debt = (
        total_existing_debt + proposed_emi
    )

    # Debt-to-Income Ratio.
    dti = total_monthly_debt / monthly_income

    # Proposed EMI as a proportion of income.
    proposed_emi_ratio = proposed_emi / monthly_income

    # Disposable income after expenses and debt repayments.
    disposable_income = (
        monthly_income
        - monthly_expenses
        - total_monthly_debt
    )

    # Debt-service capacity.
    existing_dti = total_existing_debt / monthly_income

    # Remaining debt capacity under the assumed DTI limit.
    remaining_debt_capacity = max(
        0,
        (MAX_DTI * monthly_income) - total_existing_debt
    )

    # Determine affordability.
    conditions = {
        "dti_within_limit": dti <= MAX_DTI,
        "emi_within_limit": proposed_emi_ratio <= MAX_EMI_TO_INCOME,
        "positive_disposable_income": (
            disposable_income >= MIN_DISPOSABLE_INCOME
        )
    }

    if all(conditions.values()):
        affordability_status = "Affordable"

    elif dti <= 0.50 and disposable_income > 0:
        affordability_status = "Moderate Risk"

    else:
        affordability_status = "High Risk"

    result = {
        "monthly_income": float(monthly_income),
        "monthly_expenses": float(monthly_expenses),
        "existing_emi": float(existing_emi),
        "other_monthly_debt": float(other_monthly_debt),
        "proposed_emi": float(proposed_emi),
        "total_existing_debt": float(total_existing_debt),
        "total_monthly_debt": float(total_monthly_debt),
        "existing_dti": float(existing_dti),
        "dti": float(dti),
        "proposed_emi_to_income": float(proposed_emi_ratio),
        "disposable_income": float(disposable_income),
        "remaining_debt_capacity": float(remaining_debt_capacity),
        "affordability_status": affordability_status,
        "assessment_conditions": conditions
    }

    return result


# ============================================================
# BORROWER RISK EXPLANATION
# ============================================================

def generate_explanation(result):

    explanations = []

    if not result["assessment_conditions"]["dti_within_limit"]:
        explanations.append(
            "Total debt obligations exceed the assumed "
            "40% debt-to-income threshold."
        )

    if not result["assessment_conditions"]["emi_within_limit"]:
        explanations.append(
            "Proposed EMI exceeds the assumed 30% "
            "of monthly income threshold."
        )

    if not result["assessment_conditions"]["positive_disposable_income"]:
        explanations.append(
            "Disposable income is below the configured minimum."
        )

    if not explanations:
        explanations.append(
            "The borrower meets all configured affordability checks."
        )

    return explanations


# ============================================================
# SAVE RESULTS
# ============================================================

def save_result(result):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    result["explanations"] = generate_explanation(result)

    # Save JSON.
    json_path = OUTPUT_DIR / "affordability_assessment.json"

    with open(json_path, "w") as file:
        json.dump(result, file, indent=4)

    # Save CSV.
    csv_path = METRICS_DIR / "affordability_assessment.csv"

    pd.DataFrame([result]).drop(
        columns=["assessment_conditions", "explanations"]
    ).to_csv(csv_path, index=False)

    return json_path, csv_path


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("FINAI BORROWER AFFORDABILITY ASSESSMENT")
    print("=" * 60)

    print("\nEnter borrower financial details.")
    print("All monetary values should be monthly amounts in INR.")

    try:

        monthly_income = float(
            input("\nMonthly income (₹): ")
        )

        monthly_expenses = float(
            input("Monthly household expenses (₹): ")
        )

        existing_emi = float(
            input("Existing monthly EMI (₹): ")
        )

        other_monthly_debt = float(
            input("Other monthly debt obligations (₹): ")
        )

        proposed_emi = float(
            input("Proposed loan EMI (₹): ")
        )

        result = calculate_affordability(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            existing_emi=existing_emi,
            proposed_emi=proposed_emi,
            other_monthly_debt=other_monthly_debt
        )

        json_path, csv_path = save_result(result)

        print("\n" + "=" * 60)
        print("AFFORDABILITY ASSESSMENT RESULTS")
        print("=" * 60)

        print(
            f"\nTotal Monthly Debt: "
            f"₹{result['total_monthly_debt']:,.2f}"
        )

        print(
            f"Debt-to-Income Ratio: "
            f"{result['dti'] * 100:.2f}%"
        )

        print(
            f"Proposed EMI / Income: "
            f"{result['proposed_emi_to_income'] * 100:.2f}%"
        )

        print(
            f"Disposable Income: "
            f"₹{result['disposable_income']:,.2f}"
        )

        print(
            f"Remaining Debt Capacity: "
            f"₹{result['remaining_debt_capacity']:,.2f}"
        )

        print(
            f"\nAffordability Status: "
            f"{result['affordability_status']}"
        )

        print("\nAssessment Explanation:")

        for explanation in result["explanations"]:
            print(f"- {explanation}")

        print("\nSaved files:")
        print(json_path)
        print(csv_path)

    except ValueError as error:
        print(f"\nInput error: {error}")


if __name__ == "__main__":
    main()