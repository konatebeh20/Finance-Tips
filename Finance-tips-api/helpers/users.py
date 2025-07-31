"""User-related helper functions (CRUD, auth)."""

from datetime import datetime
from typing import Optional

from flask_jwt_extended import create_access_token
from passlib.hash import bcrypt

from config.constant import ROLES
from config.db import db
from model.finance_tips import User


def hash_password(password: str) -> str:
    """Hash plaintext password using bcrypt."""
    return bcrypt.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.verify(password, hashed)


def register_user(username: str, email: str, password: str, role: str = "Entity") -> User:
    """Register a new user and return the instance."""
    if role not in ROLES:
        raise ValueError("Invalid role provided")

    if User.query.filter((User.username == username) | (User.email == email)).first():
        raise ValueError("Username or email already exists")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        created_at=datetime.utcnow(),
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(email: str, password: str) -> Optional[str]:
    """Authenticate a user. Returns JWT token if successful, else None."""
    user: User | None = User.query.filter_by(email=email).first()
    if user and verify_password(password, user.password_hash):
        # Create JWT with user identity
        token = create_access_token(identity={"id": user.id, "role": user.role})
        return token
    return None