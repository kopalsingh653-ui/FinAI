from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# BORROWER INFORMATION
# ============================================================

class BorrowerCreate(BaseModel):

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(
        min_length=2,
        max_length=150
    )

    email: Optional[str] = Field(
        default=None,
        max_length=150
    )

    monthly_income: float = Field(gt=0)

    monthly_expenses: float = Field(ge=0)

    existing_emi: float = Field(default=0, ge=0)

    other_monthly_debt: float = Field(default=0, ge=0)


# ============================================================
# LOAN INFORMATION
# ============================================================

class LoanApplicationCreate(BaseModel):

    requested_loan_amount: float = Field(gt=0)

    proposed_emi: float = Field(gt=0)


# ============================================================
# RAW CREDIT INFORMATION
# ============================================================

class CreditInput(BaseModel):

    model_config = ConfigDict(extra="forbid")

    # Personal and credit information
    LIMIT_BAL: float = Field(gt=0)
    EDUCATION: int = Field(ge=0)
    MARRIAGE: int = Field(ge=0)
    AGE: int = Field(gt=0)

    # Repayment status
    PAY_0: float
    PAY_2: float
    PAY_3: float
    PAY_4: float
    PAY_5: float
    PAY_6: float

    # Bill amounts
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float

    # Payment amounts
    PAY_AMT1: float
    PAY_AMT2: float
    PAY_AMT3: float
    PAY_AMT4: float
    PAY_AMT5: float
    PAY_AMT6: float


# ============================================================
# PREDICTION REQUEST
# ============================================================

class PredictionRequest(BaseModel):

    borrower: BorrowerCreate

    loan: LoanApplicationCreate

    credit_features: CreditInput


# ============================================================
# PREDICTION RESPONSE
# ============================================================

class PredictionResponse(BaseModel):

    borrower_reference: str

    application_reference: str

    default_probability: float

    risk_category: str

    predicted_class: int

    threshold: float

    expected_loss: float

    message: str

# ============================================================
# AFFORDABILITY REQUEST
# ============================================================

class AffordabilityRequest(BaseModel):

    monthly_income: float = Field(gt=0)

    monthly_expenses: float = Field(ge=0)

    existing_emi: float = Field(default=0, ge=0)

    other_monthly_debt: float = Field(default=0, ge=0)

    proposed_emi: float = Field(gt=0)


# ============================================================
# AFFORDABILITY RESPONSE
# ============================================================

class AffordabilityResponse(BaseModel):

    monthly_income: float

    total_monthly_debt: float

    dti: float

    proposed_emi_to_income: float

    disposable_income: float

    remaining_debt_capacity: float

    affordability_status: str

    explanations: list[str]