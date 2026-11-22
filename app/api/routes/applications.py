from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    LoanApplication,
    PredictionHistory
)

router = APIRouter(
    prefix="/api",
    tags=["Applications"]
)


@router.get("/applications")
def list_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    applications = (
        db.query(LoanApplication)
        .order_by(LoanApplication.id.desc())
        .offset(skip)
        .limit(limit)
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


@router.get("/applications/{application_id}")
def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    application = (
        db.query(LoanApplication)
        .filter(LoanApplication.id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return {
        "id": application.id,
        "application_reference": application.application_reference,
        "borrower_id": application.borrower_id,
        "requested_loan_amount": application.requested_loan_amount,
        "proposed_emi": application.proposed_emi,
        "application_status": application.application_status,
        "created_at": application.created_at
    }


@router.get("/applications/{application_id}/history")
def get_application_history(
    application_id: int,
    db: Session = Depends(get_db)
):
    application = (
        db.query(LoanApplication)
        .filter(LoanApplication.id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    history = (
        db.query(PredictionHistory)
        .filter(
            PredictionHistory.application_id == application_id
        )
        .order_by(PredictionHistory.id.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "application_id": item.application_id,
            "default_probability": item.default_probability,
            "risk_category": item.risk_category,
            "predicted_class": item.predicted_class,
            "expected_loss": item.expected_loss,
            "model_threshold": item.model_threshold,
            "created_at": item.created_at,
            "explanation": item.explanation
        }
        for item in history
    ]