from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.connection import Base


# ============================================================
# BORROWER MODEL
# ============================================================

class Borrower(Base):

    __tablename__ = "borrowers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    borrower_reference = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False
    )

    monthly_income = Column(
        Float,
        nullable=False
    )

    monthly_expenses = Column(
        Float,
        nullable=False
    )

    existing_emi = Column(
        Float,
        default=0
    )

    other_monthly_debt = Column(
        Float,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    applications = relationship(
        "LoanApplication",
        back_populates="borrower",
        cascade="all, delete-orphan"
    )

    credit_score_history = relationship(
        "CreditScoreHistory",
        back_populates="borrower",
        cascade="all, delete-orphan"
    )


# ============================================================
# LOAN APPLICATION MODEL
# ============================================================

class LoanApplication(Base):

    __tablename__ = "loan_applications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    application_reference = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    borrower_id = Column(
        Integer,
        ForeignKey("borrowers.id"),
        nullable=False,
        index=True
    )

    requested_loan_amount = Column(
        Float,
        nullable=False
    )

    proposed_emi = Column(
        Float,
        nullable=False
    )

    application_status = Column(
        String(50),
        default="Pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    borrower = relationship(
        "Borrower",
        back_populates="applications"
    )

    predictions = relationship(
        "PredictionHistory",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    credit_score_history = relationship(
        "CreditScoreHistory",
        back_populates="application"
    )


# ============================================================
# PREDICTION HISTORY MODEL
# ============================================================

class PredictionHistory(Base):

    __tablename__ = "prediction_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    application_id = Column(
        Integer,
        ForeignKey("loan_applications.id"),
        nullable=False,
        index=True
    )

    default_probability = Column(
        Float,
        nullable=False
    )

    risk_category = Column(
        String(50),
        nullable=False
    )

    predicted_class = Column(
        Integer,
        nullable=False
    )

    expected_loss = Column(
        Float,
        default=0
    )

    model_threshold = Column(
        Float,
        nullable=False
    )

    explanation = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    application = relationship(
        "LoanApplication",
        back_populates="predictions"
    )


# ============================================================
# CREDIT SCORE HISTORY MODEL
# ============================================================

class CreditScoreHistory(Base):

    __tablename__ = "credit_score_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    borrower_id = Column(
        Integer,
        ForeignKey("borrowers.id"),
        nullable=False,
        index=True
    )

    application_id = Column(
        Integer,
        ForeignKey("loan_applications.id"),
        nullable=True,
        index=True
    )

    credit_score = Column(
        Integer,
        nullable=False
    )

    score_band = Column(
        String(30),
        nullable=False
    )

    repayment_history_score = Column(
        Float,
        nullable=True
    )

    utilisation_score = Column(
        Float,
        nullable=True
    )

    payment_behaviour_score = Column(
        Float,
        nullable=True
    )

    affordability_score = Column(
        Float,
        nullable=True
    )

    debt_to_income_ratio = Column(
        Float,
        nullable=True
    )

    credit_utilisation = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    borrower = relationship(
        "Borrower",
        back_populates="credit_score_history"
    )

    application = relationship(
        "LoanApplication",
        back_populates="credit_score_history"
    )