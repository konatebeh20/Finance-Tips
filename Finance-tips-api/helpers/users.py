"""
Helper functions pour la gestion des utilisateurs
"""
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError
from config.db import db
from config.constant import ERROR_MESSAGES, USER_ROLES
from model.finance_tips import User, Role, AuditLog
import re
import secrets
import string

def validate_email(email):
    """Valide le format de l'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Valide la force du mot de passe
    Retourne (bool, message)
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not re.search(r'[0-9]', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    return True, "Mot de passe valide"

def generate_username(email):
    """Génère un nom d'utilisateur unique à partir de l'email"""
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    
    while User.query.filter_by(username=username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username

def create_user(data):
    """
    Crée un nouvel utilisateur
    Retourne (user, error_message)
    """
    try:
        # Validation des données
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not validate_email(email):
            return None, "Email invalide"
        
        valid_password, msg = validate_password(password)
        if not valid_password:
            return None, msg
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=email).first():
            return None, ERROR_MESSAGES['USER_EXISTS']
        
        # Créer l'utilisateur
        user = User(
            email=email,
            username=data.get('username', generate_username(email)),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            account_type=data.get('account_type', 'entity'),
            company_name=data.get('company_name', ''),
            company_address=data.get('company_address', ''),
            company_tax_id=data.get('company_tax_id', '')
        )
        
        user.set_password(password)
        
        # Ajouter le rôle par défaut
        default_role = Role.query.filter_by(name=USER_ROLES['USER']).first()
        if default_role:
            user.roles.append(default_role)
        
        db.session.add(user)
        db.session.commit()
        
        # Log de l'action
        log_user_action(user.id, 'USER_CREATED', 'User', user.id)
        
        return user, None
        
    except IntegrityError as e:
        db.session.rollback()
        return None, "Erreur d'intégrité des données"
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def authenticate_user(email, password):
    """
    Authentifie un utilisateur
    Retourne (user, error_message)
    """
    if not email or not password:
        return None, ERROR_MESSAGES['INVALID_CREDENTIALS']
    
    user = User.query.filter_by(email=email.lower()).first()
    
    if not user or not user.check_password(password):
        return None, ERROR_MESSAGES['INVALID_CREDENTIALS']
    
    if not user.is_active:
        return None, "Compte désactivé"
    
    # Mettre à jour la dernière connexion
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return user, None

def generate_tokens(user):
    """Génère les tokens JWT pour un utilisateur"""
    # Données à inclure dans le token
    identity = {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'account_type': user.account_type,
        'roles': [role.name for role in user.roles]
    }
    
    access_token = create_access_token(identity=user.id, additional_claims=identity)
    refresh_token = create_refresh_token(identity=user.id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }

def update_user_profile(user, data):
    """
    Met à jour le profil d'un utilisateur
    Retourne (success, error_message)
    """
    try:
        # Champs modifiables
        updatable_fields = [
            'first_name', 'last_name', 'phone',
            'company_name', 'company_address', 'company_tax_id'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Validation spéciale pour l'email
        if 'email' in data and data['email'] != user.email:
            new_email = data['email'].strip().lower()
            if not validate_email(new_email):
                return False, "Email invalide"
            
            # Vérifier l'unicité
            existing = User.query.filter_by(email=new_email).first()
            if existing and existing.id != user.id:
                return False, "Cet email est déjà utilisé"
            
            user.email = new_email
            user.is_verified = False  # Réinitialiser la vérification
        
        # Mise à jour du mot de passe
        if 'password' in data and data['password']:
            valid_password, msg = validate_password(data['password'])
            if not valid_password:
                return False, msg
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log de l'action
        log_user_action(user.id, 'PROFILE_UPDATED', 'User', user.id)
        
        return True, None
        
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_user_by_id(user_id):
    """Récupère un utilisateur par son ID"""
    return User.query.get(user_id)

def get_user_by_email(email):
    """Récupère un utilisateur par son email"""
    return User.query.filter_by(email=email.lower()).first()

def list_users(page=1, per_page=20, filters=None):
    """
    Liste les utilisateurs avec pagination et filtres
    Retourne (users, total, pages)
    """
    query = User.query
    
    if filters:
        if 'account_type' in filters:
            query = query.filter_by(account_type=filters['account_type'])
        
        if 'is_active' in filters:
            query = query.filter_by(is_active=filters['is_active'])
        
        if 'search' in filters:
            search_term = f"%{filters['search']}%"
            query = query.filter(
                db.or_(
                    User.email.ilike(search_term),
                    User.username.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.company_name.ilike(search_term)
                )
            )
    
    paginated = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return paginated.items, paginated.total, paginated.pages

def generate_verification_token():
    """Génère un token de vérification sécurisé"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def verify_user_email(user, token):
    """
    Vérifie l'email d'un utilisateur
    Retourne (success, error_message)
    """
    # TODO: Implémenter la logique de vérification avec Redis ou DB
    # Pour l'instant, on vérifie simplement
    user.is_verified = True
    db.session.commit()
    return True, None

def toggle_user_status(user):
    """Active/désactive un utilisateur"""
    user.is_active = not user.is_active
    db.session.commit()
    
    action = 'USER_ACTIVATED' if user.is_active else 'USER_DEACTIVATED'
    log_user_action(user.id, action, 'User', user.id)
    
    return user.is_active

def delete_user(user):
    """
    Supprime un utilisateur et ses données associées
    Retourne (success, error_message)
    """
    try:
        # Log avant suppression
        log_user_action(user.id, 'USER_DELETED', 'User', user.id)
        
        # La suppression en cascade est gérée par SQLAlchemy
        db.session.delete(user)
        db.session.commit()
        
        return True, None
        
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def log_user_action(user_id, action, resource_type=None, resource_id=None, data=None):
    """Enregistre une action utilisateur dans les logs d'audit"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            data=data
        )
        db.session.add(audit_log)
        db.session.commit()
    except:
        # Ne pas faire échouer l'action principale si le log échoue
        pass

def check_user_permission(user, permission):
    """
    Vérifie si un utilisateur a une permission spécifique
    TODO: Implémenter un système de permissions plus complexe
    """
    # Pour l'instant, on vérifie juste les rôles
    if permission == 'admin':
        return user.has_role('admin')
    
    return True  # Par défaut, autorisé

def get_user_statistics(user):
    """Récupère les statistiques d'un utilisateur"""
    return {
        'total_receipts': user.receipts.count(),
        'total_brands': user.brands.count(),
        'total_calculations': user.calculations.count(),
        'account_created': user.created_at.isoformat() if user.created_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'is_verified': user.is_verified,
        'is_active': user.is_active
    }