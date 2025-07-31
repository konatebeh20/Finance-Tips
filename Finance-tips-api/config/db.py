"""
Configuration de la base de données pour Finance-tips
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
import os

# Convention de nommage pour les contraintes
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

class Base(DeclarativeBase):
    metadata = metadata

# Instance SQLAlchemy
db = SQLAlchemy(model_class=Base)

def init_db(app):
    """
    Initialise la base de données avec l'application Flask
    """
    db.init_app(app)
    
    with app.app_context():
        # Créer le dossier pour SQLite si nécessaire
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        
        # Créer toutes les tables
        db.create_all()
        
        # Initialiser les données de base si nécessaire
        from model.finance_tips import User, Role
        
        # Créer les rôles de base s'ils n'existent pas
        roles = ['admin', 'user', 'premium']
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=f'{role_name.capitalize()} role')
                db.session.add(role)
        
        try:
            db.session.commit()
            print("Base de données initialisée avec succès")
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de l'initialisation de la base de données : {e}")

def get_db():
    """
    Retourne l'instance de la base de données
    """
    return db

def close_db(error=None):
    """
    Ferme la connexion à la base de données
    """
    if error:
        print(f"Erreur de base de données : {error}")
    db.session.remove()

# Fonctions utilitaires pour les transactions
def commit_changes():
    """
    Valide les changements en base de données
    """
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors du commit : {e}")
        return False

def rollback_changes():
    """
    Annule les changements en base de données
    """
    db.session.rollback()

# Décorateur pour gérer automatiquement les transactions
def transactional(func):
    """
    Décorateur pour gérer automatiquement les transactions
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise e
    return wrapper