from pydantic import BaseModel, Field


class ExpectedLossRequest(BaseModel):

    probability_of_default: float = Field(
        ge=0,
        le=1,
        description="Probability of default, between 0 and 1"
    )

    exposure_at_default: float = Field(
        ge=0,
        description="Exposure amount in INR"
    )

    loss_given_default: float = Field(
        ge=0,
        le=1,
        description="Loss fraction between 0 and 1"
    )

    annual_discount_rate: float = Field(
        default=0.10,
        ge=0,
        le=1
    )

    time_horizon_years: float = Field(
        default=1.0,
        gt=0,
        le=30
    )


class ExpectedLossResponse(BaseModel):

    probability_of_default: float
    exposure_at_default: float
    loss_given_default: float

    expected_loss: float
    discounted_expected_loss: float

    annual_discount_rate: float
    time_horizon_years: float

    methodology: str
    assumptions: list[str]