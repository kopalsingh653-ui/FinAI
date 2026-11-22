from fastapi import APIRouter, HTTPException

from app.schemas.credit_score import (
    CreditScoreRequest,
    CreditScoreResponse
)

from app.services.credit_score_service import (
    calculate_credit_score
)


router = APIRouter(
    prefix="/api",
    tags=["Credit Score"]
)


@router.post(
    "/credit-score",
    response_model=CreditScoreResponse
)
def generate_credit_score(request: CreditScoreRequest):

    try:
        result = calculate_credit_score(
            request.credit_features,
            request.financial_details
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to calculate credit score."
        )