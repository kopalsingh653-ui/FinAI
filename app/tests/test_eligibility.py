def test_credit_score_bands():

    from app.services.credit_score_service import get_score_band

    assert get_score_band(850) == "Excellent"
    assert get_score_band(775) == "Very Good"
    assert get_score_band(720) == "Good"
    assert get_score_band(670) == "Fair"
    assert get_score_band(600) == "Poor"
    assert get_score_band(400) == "Very Poor"


def test_eligibility_thresholds():

    from app.services.eligibility_service import (
        MIN_CREDIT_SCORE,
        MAX_ACCEPTABLE_PD,
        MAX_DTI
    )

    assert MIN_CREDIT_SCORE == 650
    assert MAX_ACCEPTABLE_PD == 0.25
    assert MAX_DTI == 0.40