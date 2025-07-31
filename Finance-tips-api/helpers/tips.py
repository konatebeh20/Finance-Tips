"""Halal financial calculators (no interest)."""

from __future__ import annotations

from typing import Dict


def monthly_saving_plan(target_amount: float, months: int) -> Dict[str, float]:
    """Compute the amount to save each month to reach a target.

    Returns a dict with monthly_saving and total_saved.
    """
    if months <= 0:
        raise ValueError("Months must be > 0")

    monthly = target_amount / months
    return {"monthly_saving": round(monthly, 2), "total_saved": round(target_amount, 2)}


def loan_repayment_duration(amount: float, monthly_payment: float) -> Dict[str, float]:
    """Calculate number of months required to repay a loan without interest."""
    if monthly_payment <= 0:
        raise ValueError("Monthly payment must be > 0")
    months = amount / monthly_payment
    return {"months_needed": int(months), "years": round(months / 12, 2)}


def budget_simulation(income: float, expenses: float) -> Dict[str, float]:
    """Estimate possible savings per month."""
    if income < 0 or expenses < 0:
        raise ValueError("Income and expenses must be >= 0")

    savings = income - expenses
    return {"potential_savings": round(savings, 2)}