from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    Borrower,
    LoanApplication,
    CreditScoreHistory
)

router = APIRouter(
    prefix="/api",
    tags=["Borrowers"]
)


@router.get("/borrowers")
def list_borrowers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    borrowers = (
        db.query(Borrower)
        .order_by(Borrower.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": b.id,
            "borrower_reference": b.borrower_reference,
            "full_name": b.full_name,
            "email": b.email,
            "monthly_income": b.monthly_income,
            "monthly_expenses": b.monthly_expenses,
            "existing_emi": b.existing_emi,
            "other_monthly_debt": b.other_monthly_debt,
            "created_at": b.created_at
        }
        for b in borrowers
    ]


@router.get("/borrowers/{borrower_id}")
def get_borrower(
    borrower_id: int,
    db: Session = Depends(get_db)
):
    borrower = db.query(Borrower).filter(
        Borrower.id == borrower_id
    ).first()

    if borrower is None:
        raise HTTPException(
            status_code=404,
            detail="Borrower not found"
        )

    return {
        "id": borrower.id,
        "borrower_reference": borrower.borrower_reference,
        "full_name": borrower.full_name,
        "email": borrower.email,
        "monthly_income": borrower.monthly_income,
        "monthly_expenses": borrower.monthly_expenses,
        "existing_emi": borrower.existing_emi,
        "other_monthly_debt": borrower.other_monthly_debt,
        "created_at": borrower.created_at
    }


@router.get("/borrowers/{borrower_id}/applications")
def get_borrower_applications(
    borrower_id: int,
    db: Session = Depends(get_db)
):
    borrower = db.query(Borrower).filter(
        Borrower.id == borrower_id
    ).first()

    if borrower is None:
        raise HTTPException(
            status_code=404,
            detail="Borrower not found"
        )

    applications = (
        db.query(LoanApplication)
        .filter(LoanApplication.borrower_id == borrower_id)
        .order_by(LoanApplication.id.desc())
        .all()
    )

    return [
        {
            "id": a.id,
            "application_reference": a.application_reference,
            "borrower_id": a.borrower_id,
            "requested_loan_amount": a.requested_loan_amount,
            "proposed_emi": a.proposed_emi,
            "application_status": a.application_status,
            "created_at": a.created_at
        }
        for a in applications
    ]


@router.get("/borrowers/{borrower_id}/credit-profile")
def get_credit_profile(
    borrower_id: int,
    db: Session = Depends(get_db)
):
    borrower = db.query(Borrower).filter(
        Borrower.id == borrower_id
    ).first()

    if borrower is None:
        raise HTTPException(
            status_code=404,
            detail="Borrower not found"
        )

    history = (
        db.query(CreditScoreHistory)
        .filter(CreditScoreHistory.borrower_id == borrower_id)
        .order_by(CreditScoreHistory.id.desc())
        .all()
    )

    return {
        "borrower_id": borrower.id,
        "borrower_reference": borrower.borrower_reference,
        "full_name": borrower.full_name,
        "credit_history": [
            {
                "id": item.id,
                "application_id": item.application_id,
                "credit_score": item.credit_score,
                "score_band": item.score_band,
                "repayment_history_score": item.repayment_history_score,
                "utilisation_score": item.utilisation_score,
                "payment_behaviour_score": item.payment_behaviour_score,
                "affordability_score": item.affordability_score,
                "debt_to_income_ratio": item.debt_to_income_ratio,
                "credit_utilisation": item.credit_utilisation,
                "created_at": item.created_at
            }
            for item in history
        ]
    }