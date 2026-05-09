"""Financial calculators: compound interest, loan amortization, NPV, IRR."""
from __future__ import annotations

from dataclasses import dataclass


def compound_interest(principal: float, annual_rate: float, years: float, n: int = 12) -> float:
    if principal < 0 or years < 0 or n <= 0:
        raise ValueError("principal/years must be non-negative and n > 0")
    return principal * (1 + annual_rate / n) ** (n * years)


def future_value_annuity(payment: float, annual_rate: float, years: float, n: int = 12) -> float:
    """FV of a series of equal payments made every period."""
    periods = n * years
    r = annual_rate / n
    if r == 0:
        return payment * periods
    return payment * ((1 + r) ** periods - 1) / r


@dataclass
class AmortizationRow:
    period: int
    payment: float
    interest: float
    principal: float
    balance: float


def loan_payment(principal: float, annual_rate: float, years: float, n: int = 12) -> float:
    periods = int(round(n * years))
    r = annual_rate / n
    if periods <= 0:
        raise ValueError("loan term must be positive")
    if r == 0:
        return principal / periods
    return principal * r * (1 + r) ** periods / ((1 + r) ** periods - 1)


def amortization_schedule(
    principal: float, annual_rate: float, years: float, n: int = 12
) -> list[AmortizationRow]:
    periods = int(round(n * years))
    r = annual_rate / n
    pmt = loan_payment(principal, annual_rate, years, n)
    balance = principal
    schedule: list[AmortizationRow] = []
    for period in range(1, periods + 1):
        interest = balance * r
        principal_paid = pmt - interest
        balance = max(0.0, balance - principal_paid)
        schedule.append(AmortizationRow(period, pmt, interest, principal_paid, balance))
    return schedule


def npv(rate: float, cashflows: list[float]) -> float:
    """Net present value. cashflows[0] is t=0 (typically negative for an outlay)."""
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))


def irr(cashflows: list[float], guess: float = 0.1, tol: float = 1e-7, max_iter: int = 200) -> float:
    """Internal rate of return via Newton's method; falls back to bisection."""
    if not cashflows or all(cf >= 0 for cf in cashflows) or all(cf <= 0 for cf in cashflows):
        raise ValueError("cashflows must contain at least one positive and one negative value")

    rate = guess
    for _ in range(max_iter):
        f = sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))
        df = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cashflows))
        if df == 0:
            break
        new_rate = rate - f / df
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate

    lo, hi = -0.999, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(mid, cashflows) > 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            return mid
    raise RuntimeError("IRR did not converge")


def retirement_target(
    current_savings: float,
    annual_contribution: float,
    annual_rate: float,
    years: float,
) -> float:
    """Projected balance after `years`, contributing once per year at year-end."""
    fv_savings = current_savings * (1 + annual_rate) ** years
    fv_contrib = future_value_annuity(annual_contribution, annual_rate, years, n=1)
    return fv_savings + fv_contrib
