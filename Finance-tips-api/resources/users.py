"""User authentication routes."""

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, Unauthorized

from helpers.users import authenticate_user, register_user

users_bp = Blueprint("users", __name__)


@users_bp.post("/register")
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "Entity")

    if not all([username, email, password]):
        raise BadRequest("Username, email, and password are required")

    try:
        user = register_user(username, email, password, role)
        return jsonify({"id": user.id, "username": user.username, "email": user.email}), 201
    except ValueError as exc:
        raise BadRequest(str(exc)) from exc


@users_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        raise BadRequest("Email and password are required")

    token = authenticate_user(email, password)
    if not token:
        raise Unauthorized("Invalid credentials")

    return jsonify({"access_token": token})