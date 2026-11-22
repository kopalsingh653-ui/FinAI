def calculate_expected_credit_loss(
    probability_of_default,
    exposure_at_default,
    loss_given_default,
    annual_discount_rate=0.10,
    time_horizon_years=1.0
):
    """
    Calculate simplified illustrative Expected Credit Loss.

    PD and LGD are fractions between 0 and 1.
    EAD is expressed in INR.
    """

    pd_value = float(probability_of_default)
    ead_value = float(exposure_at_default)
    lgd_value = float(loss_given_default)

    discount_rate = float(annual_discount_rate)
    horizon = float(time_horizon_years)

    if not 0 <= pd_value <= 1:
        raise ValueError("PD must be between 0 and 1.")

    if ead_value < 0:
        raise ValueError("EAD cannot be negative.")

    if not 0 <= lgd_value <= 1:
        raise ValueError("LGD must be between 0 and 1.")

    if not 0 <= discount_rate <= 1:
        raise ValueError("Discount rate must be between 0 and 1.")

    if horizon <= 0:
        raise ValueError("Time horizon must be positive.")

    # Simplified expected loss calculation.
    expected_loss = (
        pd_value * lgd_value * ead_value
    )

    # Illustrative discounting.
    discounted_expected_loss = (
        expected_loss /
        ((1 + discount_rate) ** horizon)
    )

    return {
        "probability_of_default": pd_value,
        "exposure_at_default": ead_value,
        "loss_given_default": lgd_value,
        "expected_loss": expected_loss,
        "discounted_expected_loss": discounted_expected_loss,
        "annual_discount_rate": discount_rate,
        "time_horizon_years": horizon,
        "methodology": "Simplified PD × LGD × EAD",
        "assumptions": [
            "PD is supplied as a probability between 0 and 1.",
            "LGD is supplied as a fraction between 0 and 1.",
            "EAD is supplied in INR.",
            "Discounting uses an illustrative annual rate.",
            "This is not a complete IFRS 9 staging or lifetime ECL model."
        ]
    }