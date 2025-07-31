"""
Configuration des constantes pour l'application Finance-tips
"""
import os
from datetime import timedelta

# Configuration de base
APP_NAME = "Finance-tips"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Application de gestion financière halal pour PME et particuliers"

# Configuration Flask
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this-in-production')
DEBUG = FLASK_ENV == 'development'

# Configuration JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
JWT_ALGORITHM = 'HS256'

# Configuration Base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finance_tips.db')
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = DEBUG

# Configuration CORS
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Configuration Email (pour newsletter)
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@finance-tips.com')

# Configuration Upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'statics', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

# Configuration des types de comptes
ACCOUNT_TYPES = {
    'COMPANY': 'company',
    'ENTITY': 'entity'
}

# Configuration des rôles
USER_ROLES = {
    'ADMIN': 'admin',
    'USER': 'user',
    'PREMIUM': 'premium'
}

# Constantes pour les calculs financiers halal
HALAL_FINANCE = {
    'MIN_MONTHLY_SAVING': 10,  # Épargne minimale mensuelle
    'MAX_LOAN_DURATION_MONTHS': 360,  # Durée max de remboursement (30 ans)
    'MIN_LOAN_AMOUNT': 100,  # Montant minimum d'emprunt
    'MAX_LOAN_AMOUNT': 10000000,  # Montant maximum d'emprunt
}

# Configuration des couleurs du thème
THEME_COLORS = {
    'PRIMARY': '#2D6A9F',  # Bleu mi-sombre pour titres
    'SECONDARY': '#85B6D1',  # Bleu clair pour fonds/boutons
    'SUCCESS': '#28a745',
    'DANGER': '#dc3545',
    'WARNING': '#ffc107',
    'INFO': '#17a2b8',
    'LIGHT': '#f8f9fa',
    'DARK': '#343a40'
}

# Configuration pagination
PAGINATION = {
    'DEFAULT_PAGE': 1,
    'DEFAULT_PER_PAGE': 20,
    'MAX_PER_PAGE': 100
}

# Messages d'erreur standards
ERROR_MESSAGES = {
    'UNAUTHORIZED': 'Accès non autorisé',
    'INVALID_CREDENTIALS': 'Identifiants invalides',
    'USER_EXISTS': 'Cet utilisateur existe déjà',
    'NOT_FOUND': 'Ressource non trouvée',
    'INVALID_DATA': 'Données invalides',
    'SERVER_ERROR': 'Erreur serveur'
}

# Configuration des templates de reçus
RECEIPT_TEMPLATES = {
    'SIMPLE': 'simple',
    'PROFESSIONAL': 'professional',
    'CUSTOM': 'custom'
}

# Configuration des devises
CURRENCIES = {
    'EUR': {'symbol': '€', 'name': 'Euro'},
    'USD': {'symbol': '$', 'name': 'Dollar US'},
    'MAD': {'symbol': 'DH', 'name': 'Dirham Marocain'},
    'TND': {'symbol': 'DT', 'name': 'Dinar Tunisien'},
    'DZD': {'symbol': 'DA', 'name': 'Dinar Algérien'}
}