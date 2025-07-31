"""
Application principale Finance-tips API
"""
import os
import logging
from datetime import datetime
from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Importer la configuration
from config.constant import *
from config.db import init_db, close_db

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Factory pour créer l'application Flask"""
    
    # Créer l'application Flask
    app = Flask(__name__)
    
    # Configuration de l'application
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=SQLALCHEMY_TRACK_MODIFICATIONS,
        JWT_SECRET_KEY=JWT_SECRET_KEY,
        JWT_ACCESS_TOKEN_EXPIRES=JWT_ACCESS_TOKEN_EXPIRES,
        JWT_REFRESH_TOKEN_EXPIRES=JWT_REFRESH_TOKEN_EXPIRES,
        JWT_ALGORITHM=JWT_ALGORITHM,
        MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH
    )
    
    # Initialiser les extensions
    CORS(app, origins=CORS_ORIGINS)
    jwt = JWTManager(app)
    api = Api(app)
    
    # Initialiser la base de données
    init_db(app)
    
    # Enregistrer les routes
    from resources.users import register_user_routes
    from resources.tips import register_tips_routes
    
    register_user_routes(api)
    register_tips_routes(api)
    
    # Route de base
    @app.route('/')
    def index():
        return jsonify({
            'app': APP_NAME,
            'version': APP_VERSION,
            'description': APP_DESCRIPTION,
            'endpoints': {
                'auth': {
                    'register': '/api/users/register',
                    'login': '/api/users/login'
                },
                'calculators': {
                    'savings_plan': '/api/calculators/savings-plan',
                    'loan_duration': '/api/calculators/loan-duration',
                    'budget_simulation': '/api/calculators/budget-simulation',
                    'zakat': '/api/calculators/zakat'
                },
                'docs': '/api/docs'
            }
        })
    
    # Route de santé
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Gestion des erreurs JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token expiré',
            'message': 'Veuillez vous reconnecter'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Token invalide',
            'message': 'Le token fourni est invalide'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Autorisation requise',
            'message': 'Un token valide est requis pour accéder à cette ressource'
        }), 401
    
    # Gestionnaire d'erreurs global
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Ressource non trouvée',
            'message': 'La ressource demandée n\'existe pas'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Erreur serveur : {error}")
        return jsonify({
            'error': 'Erreur serveur',
            'message': 'Une erreur interne s\'est produite'
        }), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'error': 'Fichier trop volumineux',
            'message': f'La taille maximale autorisée est {MAX_CONTENT_LENGTH / 1024 / 1024}MB'
        }), 413
    
    # Middleware pour logger les requêtes
    @app.before_request
    def log_request():
        from flask import request
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    # Middleware pour fermer la connexion DB
    @app.teardown_appcontext
    def teardown_db(error):
        close_db(error)
    
    # Créer les dossiers nécessaires
    os.makedirs('log', exist_ok=True)
    os.makedirs('statics/uploads', exist_ok=True)
    
    logger.info(f"Application {APP_NAME} v{APP_VERSION} créée avec succès")
    
    return app

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # Configuration pour le développement
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Démarrage de l'application sur {host}:{port}")
    
    # Lancer l'application
    app.run(
        host=host,
        port=port,
        debug=DEBUG,
        use_reloader=DEBUG
    )