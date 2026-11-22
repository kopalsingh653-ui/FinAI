import uuid
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db

from app.database.models import (
    Borrower,
    LoanApplication,
    PredictionHistory
)

from app.schemas.borrower import (
    PredictionRequest,
    PredictionResponse
)

from app.services.prediction_service import generate_prediction


router = APIRouter(
    prefix="/api",
    tags=["Credit Risk Prediction"]
)


def generate_reference(prefix):

    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


@router.post(
    "/predict",
    response_model=PredictionResponse
)
def predict_credit_risk(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):

    try:

        # 1. Convert validated credit input to dictionary.
        credit_data = request.credit_features.model_dump()

        # 2. Generate model prediction.
        prediction = generate_prediction(
            credit_features=credit_data,
            requested_loan_amount=request.loan.requested_loan_amount
        )

        # 3. Create borrower.
        borrower = Borrower(
            borrower_reference=generate_reference("BOR"),
            full_name=request.borrower.full_name,
            email=request.borrower.email,
            monthly_income=request.borrower.monthly_income,
            monthly_expenses=request.borrower.monthly_expenses,
            existing_emi=request.borrower.existing_emi,
            other_monthly_debt=request.borrower.other_monthly_debt
        )

        db.add(borrower)
        db.flush()

        # 4. Create loan application.
        application = LoanApplication(
            application_reference=generate_reference("APP"),
            borrower_id=borrower.id,
            requested_loan_amount=request.loan.requested_loan_amount,
            proposed_emi=request.loan.proposed_emi,
            application_status="PENDING"
        )

        db.add(application)
        db.flush()

        # 5. Save prediction history.
        history = PredictionHistory(
            application_id=application.id,
            default_probability=prediction["default_probability"],
            risk_category=prediction["risk_category"],
            predicted_class=prediction["predicted_class"],
            expected_loss=prediction["expected_loss"],
            model_threshold=prediction["threshold"],
            explanation=json.dumps({
                "lgd_assumption": prediction["lgd_assumption"],
                "ead_assumption": prediction["ead_assumption"]
            })
        )

        db.add(history)

        # Commit all records together.
        db.commit()

        return PredictionResponse(
            borrower_reference=borrower.borrower_reference,
            application_reference=application.application_reference,
            default_probability=prediction["default_probability"],
            risk_category=prediction["risk_category"],
            predicted_class=prediction["predicted_class"],
            threshold=prediction["threshold"],
            expected_loss=prediction["expected_loss"],
            message=(
                "Credit risk assessment completed. "
                "This is a decision-support estimate, "
                "not an automatic lending decision."
            )
        )

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database operation failed."
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="An unexpected prediction error occurred."
        )