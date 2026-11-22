from fastapi import APIRouter, HTTPException

from app.schemas.borrower import (
    AffordabilityRequest,
    AffordabilityResponse
)

from app.services.affordability_service import (
    assess_borrower_affordability
)


router = APIRouter(
    prefix="/api",
    tags=["Affordability Assessment"]
)


@router.post(
    "/affordability",
    response_model=AffordabilityResponse
)
def assess_affordability(request: AffordabilityRequest):

    try:

        result = assess_borrower_affordability(
            monthly_income=request.monthly_income,
            monthly_expenses=request.monthly_expenses,
            existing_emi=request.existing_emi,
            proposed_emi=request.proposed_emi,
            other_monthly_debt=request.other_monthly_debt
        )

        return AffordabilityResponse(
            monthly_income=result["monthly_income"],
            total_monthly_debt=result["total_monthly_debt"],
            dti=result["dti"],
            proposed_emi_to_income=result["proposed_emi_to_income"],
            disposable_income=result["disposable_income"],
            remaining_debt_capacity=result["remaining_debt_capacity"],
            affordability_status=result["affordability_status"],
            explanations=result["explanations"]
        )

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Affordability assessment could not be completed."
        )