from flask import Flask
import os
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config.db import db, init_db
from resources.users import users_bp
from resources.tips import tips_bp


def create_app():
    """Application factory."""
    app = Flask(__name__)

    # Basic configuration – override with environment variables if defined
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///finance_tips.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "change_this_secret"),
    )

    # Extensions
    CORS(app)
    db.init_app(app)
    JWTManager(app)

    # Blueprints / routes
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(tips_bp, url_prefix="/api/tips")

    # Create tables if they do not exist
    with app.app_context():
        init_db()

    return app


if __name__ == "__main__":
    import os

    app = create_app()
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(debug=debug_mode)