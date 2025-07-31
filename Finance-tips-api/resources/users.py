"""
Endpoints API pour la gestion des utilisateurs
"""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers.users import (
    create_user, authenticate_user, generate_tokens,
    update_user_profile, get_user_by_id, list_users,
    toggle_user_status, delete_user, get_user_statistics
)
from config.constant import ERROR_MESSAGES, PAGINATION
import logging

logger = logging.getLogger(__name__)

class UserRegister(Resource):
    """Endpoint pour l'inscription des utilisateurs"""
    
    def post(self):
        """Créer un nouveau compte utilisateur"""
        try:
            data = request.get_json()
            
            # Validation des données requises
            required_fields = ['email', 'password']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Le champ {field} est requis'}, 400
            
            # Validation du type de compte
            account_type = data.get('account_type', 'entity')
            if account_type not in ['company', 'entity']:
                return {'error': 'Type de compte invalide'}, 400
            
            # Si c'est un compte entreprise, vérifier les champs supplémentaires
            if account_type == 'company' and not data.get('company_name'):
                return {'error': 'Le nom de l\'entreprise est requis pour un compte company'}, 400
            
            # Créer l'utilisateur
            user, error = create_user(data)
            
            if error:
                return {'error': error}, 400
            
            # Générer les tokens
            tokens = generate_tokens(user)
            
            return {
                'message': 'Compte créé avec succès',
                'user': user.to_dict(),
                **tokens
            }, 201
            
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class UserLogin(Resource):
    """Endpoint pour la connexion des utilisateurs"""
    
    def post(self):
        """Authentifier un utilisateur"""
        try:
            data = request.get_json()
            
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return {'error': 'Email et mot de passe requis'}, 400
            
            # Authentifier l'utilisateur
            user, error = authenticate_user(email, password)
            
            if error:
                return {'error': error}, 401
            
            # Générer les tokens
            tokens = generate_tokens(user)
            
            return {
                'message': 'Connexion réussie',
                'user': user.to_dict(),
                **tokens
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class UserProfile(Resource):
    """Endpoint pour la gestion du profil utilisateur"""
    
    @jwt_required()
    def get(self):
        """Récupérer le profil de l'utilisateur connecté"""
        try:
            user_id = get_jwt_identity()
            user = get_user_by_id(user_id)
            
            if not user:
                return {'error': ERROR_MESSAGES['NOT_FOUND']}, 404
            
            return {
                'user': user.to_dict(),
                'statistics': get_user_statistics(user)
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du profil : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500
    
    @jwt_required()
    def put(self):
        """Mettre à jour le profil de l'utilisateur connecté"""
        try:
            user_id = get_jwt_identity()
            user = get_user_by_id(user_id)
            
            if not user:
                return {'error': ERROR_MESSAGES['NOT_FOUND']}, 404
            
            data = request.get_json()
            
            # Mettre à jour le profil
            success, error = update_user_profile(user, data)
            
            if not success:
                return {'error': error}, 400
            
            return {
                'message': 'Profil mis à jour avec succès',
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du profil : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500
    
    @jwt_required()
    def delete(self):
        """Supprimer le compte de l'utilisateur connecté"""
        try:
            user_id = get_jwt_identity()
            user = get_user_by_id(user_id)
            
            if not user:
                return {'error': ERROR_MESSAGES['NOT_FOUND']}, 404
            
            success, error = delete_user(user)
            
            if not success:
                return {'error': error}, 400
            
            return {'message': 'Compte supprimé avec succès'}, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du compte : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class UserDetail(Resource):
    """Endpoint pour la gestion d'un utilisateur spécifique (admin)"""
    
    @jwt_required()
    def get(self, user_id):
        """Récupérer les détails d'un utilisateur"""
        try:
            # TODO: Vérifier les permissions admin
            user = get_user_by_id(user_id)
            
            if not user:
                return {'error': ERROR_MESSAGES['NOT_FOUND']}, 404
            
            return {
                'user': user.to_dict(),
                'statistics': get_user_statistics(user)
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500
    
    @jwt_required()
    def put(self, user_id):
        """Mettre à jour un utilisateur (admin)"""
        try:
            # TODO: Vérifier les permissions admin
            user = get_user_by_id(user_id)
            
            if not user:
                return {'error': ERROR_MESSAGES['NOT_FOUND']}, 404
            
            data = request.get_json()
            
            # Actions spéciales admin
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            if 'is_verified' in data:
                user.is_verified = data['is_verified']
            
            # Mettre à jour le profil
            success, error = update_user_profile(user, data)
            
            if not success:
                return {'error': error}, 400
            
            return {
                'message': 'Utilisateur mis à jour avec succès',
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'utilisateur : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class UserList(Resource):
    """Endpoint pour lister les utilisateurs (admin)"""
    
    @jwt_required()
    def get(self):
        """Lister tous les utilisateurs avec pagination"""
        try:
            # TODO: Vérifier les permissions admin
            
            # Récupérer les paramètres de pagination
            page = request.args.get('page', PAGINATION['DEFAULT_PAGE'], type=int)
            per_page = request.args.get('per_page', PAGINATION['DEFAULT_PER_PAGE'], type=int)
            per_page = min(per_page, PAGINATION['MAX_PER_PAGE'])
            
            # Récupérer les filtres
            filters = {}
            if request.args.get('account_type'):
                filters['account_type'] = request.args.get('account_type')
            
            if request.args.get('is_active') is not None:
                filters['is_active'] = request.args.get('is_active', type=bool)
            
            if request.args.get('search'):
                filters['search'] = request.args.get('search')
            
            # Récupérer les utilisateurs
            users, total, pages = list_users(page, per_page, filters)
            
            return {
                'users': [user.to_dict() for user in users],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': pages
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class UserToggleStatus(Resource):
    """Endpoint pour activer/désactiver un utilisateur"""
    
    @jwt_required()
    def post(self, user_id):
        """Activer ou désactiver un utilisateur"""
        try:
            # TODO: Vérifier les permissions admin
            user = get_user_by_id(user_id)
            
            if not user:
                return {'error': ERROR_MESSAGES['NOT_FOUND']}, 404
            
            new_status = toggle_user_status(user)
            
            return {
                'message': f"Utilisateur {'activé' if new_status else 'désactivé'} avec succès",
                'is_active': new_status
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors du changement de statut : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class UserStatistics(Resource):
    """Endpoint pour les statistiques utilisateur"""
    
    @jwt_required()
    def get(self):
        """Récupérer les statistiques de l'utilisateur connecté"""
        try:
            user_id = get_jwt_identity()
            user = get_user_by_id(user_id)
            
            if not user:
                return {'error': ERROR_MESSAGES['NOT_FOUND']}, 404
            
            stats = get_user_statistics(user)
            
            return {'statistics': stats}, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

# Fonction pour enregistrer toutes les routes utilisateur
def register_user_routes(api):
    """Enregistre toutes les routes utilisateur"""
    api.add_resource(UserRegister, '/api/users/register')
    api.add_resource(UserLogin, '/api/users/login')
    api.add_resource(UserProfile, '/api/users/profile')
    api.add_resource(UserDetail, '/api/users/<int:user_id>')
    api.add_resource(UserList, '/api/users')
    api.add_resource(UserToggleStatus, '/api/users/<int:user_id>/toggle-status')
    api.add_resource(UserStatistics, '/api/users/statistics')