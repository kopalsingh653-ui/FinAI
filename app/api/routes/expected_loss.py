from fastapi import APIRouter, HTTPException

from app.schemas.risk import (
    ExpectedLossRequest,
    ExpectedLossResponse
)

from app.services.risk_service import (
    calculate_expected_credit_loss
)


router = APIRouter(
    prefix="/api",
    tags=["Expected Credit Loss"]
)


@router.post(
    "/expected-loss",
    response_model=ExpectedLossResponse
)
def calculate_expected_loss(request: ExpectedLossRequest):

    try:

        result = calculate_expected_credit_loss(
            probability_of_default=request.probability_of_default,
            exposure_at_default=request.exposure_at_default,
            loss_given_default=request.loss_given_default,
            annual_discount_rate=request.annual_discount_rate,
            time_horizon_years=request.time_horizon_years
        )

        return ExpectedLossResponse(**result)

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Expected credit loss calculation failed."
        )