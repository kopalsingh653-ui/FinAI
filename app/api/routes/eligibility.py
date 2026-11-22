import uuid
import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db

from app.database.models import (
    Borrower,
    LoanApplication,
    PredictionHistory,
    CreditScoreHistory
)

from app.schemas.credit_score import (
    EligibilityRequest,
    EligibilityResponse
)

from app.services.eligibility_service import (
    calculate_eligibility
)


# ============================================================
# LOGGER CONFIGURATION
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# ROUTER CONFIGURATION
# ============================================================

router = APIRouter(
    prefix="/api",
    tags=["Loan Eligibility"]
)


# ============================================================
# REFERENCE GENERATOR
# ============================================================

def generate_reference(prefix: str) -> str:

    unique_id = uuid.uuid4().hex[:12].upper()

    return f"{prefix}-{unique_id}"


# ============================================================
# LOAN ELIGIBILITY ENDPOINT
# ============================================================

@router.post(
    "/eligibility",
    response_model=EligibilityResponse
)
def check_loan_eligibility(
    request: EligibilityRequest,
    db: Session = Depends(get_db)
):

    try:

        # ----------------------------------------------------
        # 1. CALCULATE ELIGIBILITY
        # ----------------------------------------------------

        logger.info("Starting eligibility assessment")

        result = calculate_eligibility(request)

        credit_details = result.pop(
            "_credit_score_details"
        )

        predicted_class = result.pop(
            "_predicted_class"
        )

        model_threshold = result.pop(
            "_model_threshold"
        )

        logger.info("Eligibility calculation completed")

        # ----------------------------------------------------
        # 2. FIND EXISTING BORROWER
        # ----------------------------------------------------

        borrower = (
            db.query(Borrower)
            .filter(
                Borrower.email == str(request.borrower.email)
            )
            .first()
        )

        # ----------------------------------------------------
        # 3. CREATE OR UPDATE BORROWER
        # ----------------------------------------------------

        if borrower is None:

            borrower = Borrower(

                borrower_reference=generate_reference("BRW"),

                full_name=request.borrower.full_name,

                email=str(request.borrower.email),

                monthly_income=request.financial_details.monthly_income,

                monthly_expenses=request.financial_details.monthly_expenses,

                existing_emi=request.financial_details.existing_emi,

                other_monthly_debt=request.financial_details.other_monthly_debt

            )

            db.add(borrower)

            db.flush()

            logger.info(
                "New borrower created: %s",
                borrower.borrower_reference
            )

        else:

            borrower.full_name = request.borrower.full_name

            borrower.monthly_income = (
                request.financial_details.monthly_income
            )

            borrower.monthly_expenses = (
                request.financial_details.monthly_expenses
            )

            borrower.existing_emi = (
                request.financial_details.existing_emi
            )

            borrower.other_monthly_debt = (
                request.financial_details.other_monthly_debt
            )

            logger.info(
                "Existing borrower found: %s",
                borrower.borrower_reference
            )

        # ----------------------------------------------------
        # 4. CREATE LOAN APPLICATION
        # ----------------------------------------------------

        application = LoanApplication(

            application_reference=generate_reference("APP"),

            borrower_id=borrower.id,

            requested_loan_amount=request.requested_loan_amount,

            proposed_emi=request.proposed_emi,

            application_status=result["eligibility_status"]

        )

        db.add(application)

        db.flush()

        logger.info(
            "Loan application created: %s",
            application.application_reference
        )

        # ----------------------------------------------------
        # 5. SAVE CREDIT SCORE HISTORY
        # ----------------------------------------------------

        score_history = CreditScoreHistory(

            borrower_id=borrower.id,

            application_id=application.id,

            credit_score=credit_details["credit_score"],

            score_band=credit_details["score_band"],

            repayment_history_score=credit_details[
                "repayment_history_score"
            ],

            utilisation_score=credit_details[
                "utilisation_score"
            ],

            payment_behaviour_score=credit_details[
                "payment_behaviour_score"
            ],

            affordability_score=credit_details[
                "affordability_score"
            ],

            debt_to_income_ratio=credit_details[
                "debt_to_income_ratio"
            ],

            credit_utilisation=credit_details[
                "credit_utilisation"
            ]

        )

        db.add(score_history)

        logger.info("Credit score history added")

        # ----------------------------------------------------
        # 6. SAVE PREDICTION HISTORY
        # ----------------------------------------------------

        prediction_history = PredictionHistory(

            application_id=application.id,

            default_probability=result["default_probability"],

            risk_category=result["risk_category"],

            predicted_class=predicted_class,

            expected_loss=result["expected_loss"],

            model_threshold=model_threshold,

            explanation="; ".join(
                result["eligibility_reason"]
            )

        )

        db.add(prediction_history)

        logger.info("Prediction history added")

        # ----------------------------------------------------
        # 7. COMMIT DATABASE TRANSACTION
        # ----------------------------------------------------

        db.commit()

        # Refresh records to ensure generated values are available.
        db.refresh(borrower)
        db.refresh(application)

        logger.info(
            "Eligibility assessment successfully saved"
        )

        # ----------------------------------------------------
        # 8. ADD DATABASE REFERENCES TO RESPONSE
        # ----------------------------------------------------

        result["borrower_id"] = borrower.id

        result["borrower_reference"] = (
            borrower.borrower_reference
        )

        result["application_id"] = application.id

        result["application_reference"] = (
            application.application_reference
        )

        return result

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except ValueError as error:

        db.rollback()

        logger.warning(
            "Eligibility validation error: %s",
            error
        )

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except SQLAlchemyError as error:

        db.rollback()

        logger.exception(
            "Database error during eligibility assessment: %s",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Database error while saving eligibility assessment. Check backend logs."
        )

    except Exception as error:

        db.rollback()

        logger.exception(
            "Unexpected eligibility assessment error: %s",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Eligibility assessment failed. Check backend logs."
        )