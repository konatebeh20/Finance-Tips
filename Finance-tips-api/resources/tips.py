"""Financial calculators routes."""

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from helpers.tips import budget_simulation, loan_repayment_duration, monthly_saving_plan

tips_bp = Blueprint("tips", __name__)


@tips_bp.post("/saving-plan")
def saving_plan():
    data = request.get_json() or {}
    target = data.get("target_amount")
    months = data.get("months")

    if target is None or months is None:
        raise BadRequest("target_amount and months are required")

    try:
        result = monthly_saving_plan(float(target), int(months))
    except ValueError as exc:
        raise BadRequest(str(exc)) from exc

    return jsonify(result)


@tips_bp.post("/loan-duration")
def loan_duration():
    data = request.get_json() or {}
    amount = data.get("amount")
    monthly_payment = data.get("monthly_payment")

    if amount is None or monthly_payment is None:
        raise BadRequest("amount and monthly_payment are required")

    try:
        result = loan_repayment_duration(float(amount), float(monthly_payment))
    except ValueError as exc:
        raise BadRequest(str(exc)) from exc

    return jsonify(result)


@tips_bp.post("/budget-simulation")
def budget():
    data = request.get_json() or {}
    income = data.get("income")
    expenses = data.get("expenses")

    if income is None or expenses is None:
        raise BadRequest("income and expenses are required")

    try:
        result = budget_simulation(float(income), float(expenses))
    except ValueError as exc:
        raise BadRequest(str(exc)) from exc

    return jsonify(result)