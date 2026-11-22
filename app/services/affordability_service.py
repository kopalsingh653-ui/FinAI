from src.affordability import (
    calculate_affordability,
    generate_explanation
)


def assess_borrower_affordability(
    monthly_income,
    monthly_expenses,
    existing_emi,
    proposed_emi,
    other_monthly_debt=0
):
    """
    Run the existing FinAI affordability assessment
    and return API-ready results.
    """

    result = calculate_affordability(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        existing_emi=existing_emi,
        proposed_emi=proposed_emi,
        other_monthly_debt=other_monthly_debt
    )

    result["explanations"] = generate_explanation(result)

    return result