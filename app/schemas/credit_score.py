from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.borrower import CreditInput


class BorrowerFinancialDetails(BaseModel):
    monthly_income: float = Field(gt=0)
    monthly_expenses: float = Field(ge=0)
    existing_emi: float = Field(ge=0)
    other_monthly_debt: float = Field(default=0, ge=0)


class CreditScoreRequest(BaseModel):
    credit_features: CreditInput
    financial_details: BorrowerFinancialDetails


class CreditScoreResponse(BaseModel):
    credit_score: int
    score_band: str

    repayment_history_score: float
    utilisation_score: float
    payment_behaviour_score: float
    affordability_score: float

    debt_to_income_ratio: float
    credit_utilisation: float

    strengths: list[str]
    risk_factors: list[str]

    methodology: str


class EligibilityRequest(BaseModel):
    credit_features: CreditInput
    financial_details: BorrowerFinancialDetails

    requested_loan_amount: float = Field(gt=0)
    proposed_emi: float = Field(gt=0)


class EligibilityResponse(BaseModel):
    credit_score: int
    score_band: str

    default_probability: float
    risk_category: str

    debt_to_income_ratio: float
    proposed_emi_ratio: float
    disposable_income: float

    eligibility_status: str
    eligibility_reason: list[str]
    recommendations: list[str]

    disclaimer: str

from pydantic import BaseModel, Field, EmailStr

from app.schemas.borrower import CreditInput


class BorrowerIdentity(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr


class BorrowerFinancialDetails(BaseModel):
    monthly_income: float = Field(gt=0)
    monthly_expenses: float = Field(ge=0)
    existing_emi: float = Field(ge=0)
    other_monthly_debt: float = Field(default=0, ge=0)


class EligibilityRequest(BaseModel):
    borrower: BorrowerIdentity
    credit_features: CreditInput
    financial_details: BorrowerFinancialDetails

    requested_loan_amount: float = Field(gt=0)
    proposed_emi: float = Field(gt=0)