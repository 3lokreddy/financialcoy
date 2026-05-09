import math

import pytest

from financialcoy import calc


def test_compound_interest_zero_rate():
    assert calc.compound_interest(1000, 0.0, 5) == pytest.approx(1000)


def test_compound_interest_known_value():
    fv = calc.compound_interest(1000, 0.05, 10, n=1)
    assert fv == pytest.approx(1000 * 1.05**10)


def test_loan_payment_zero_rate():
    pmt = calc.loan_payment(1200, 0.0, 1, n=12)
    assert pmt == pytest.approx(100.0)


def test_amortization_pays_off_loan():
    schedule = calc.amortization_schedule(10000, 0.05, 2, n=12)
    assert len(schedule) == 24
    assert schedule[-1].balance == pytest.approx(0.0, abs=1e-2)


def test_npv_simple():
    assert calc.npv(0.0, [-100, 50, 50, 50]) == pytest.approx(50.0)


def test_irr_recovers_known_rate():
    cashflows = [-1000, 100, 200, 300, 400, 500]
    rate = calc.irr(cashflows)
    assert calc.npv(rate, cashflows) == pytest.approx(0.0, abs=1e-4)


def test_irr_requires_sign_change():
    with pytest.raises(ValueError):
        calc.irr([100, 200, 300])


def test_retirement_grows():
    fv = calc.retirement_target(10000, 6000, 0.06, 30)
    assert fv > 10000 + 6000 * 30
    assert math.isfinite(fv)
