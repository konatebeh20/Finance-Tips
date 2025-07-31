"""Database configuration and helpers."""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance used across the application
# Imported by models and app factory

db = SQLAlchemy()


def init_db():
    """Create database tables for all registered models."""
    # Import models inside the function to avoid circular imports
    from model import finance_tips  # noqa: F401  pylint: disable=unused-import

    db.create_all()