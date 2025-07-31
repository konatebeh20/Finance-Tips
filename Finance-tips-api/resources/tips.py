"""
Endpoints API pour les calculs financiers et les conseils
"""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers.tips import (
    calculate_savings_plan, calculate_loan_duration, simulate_budget,
    save_calculation, get_user_calculations, get_financial_tips,
    increment_tip_views, calculate_zakat
)
from helpers.users import get_user_by_id
from config.constant import ERROR_MESSAGES, PAGINATION
import logging

logger = logging.getLogger(__name__)

class SavingsPlanCalculator(Resource):
    """Endpoint pour le calcul du plan d'épargne"""
    
    def post(self):
        """Calculer un plan d'épargne halal"""
        try:
            data = request.get_json()
            
            target_amount = data.get('target_amount')
            if not target_amount:
                return {'error': 'Le montant cible est requis'}, 400
            
            monthly_saving = data.get('monthly_saving')
            duration_months = data.get('duration_months')
            
            # Calculer le plan d'épargne
            result = calculate_savings_plan(
                float(target_amount),
                float(monthly_saving) if monthly_saving else None,
                int(duration_months) if duration_months else None
            )
            
            if result.get('error'):
                return {'error': result['error']}, 400
            
            # Sauvegarder le calcul si l'utilisateur est connecté
            user_id = get_jwt_identity() if request.headers.get('Authorization') else None
            if user_id:
                save_calculation(
                    user_id,
                    'savings_plan',
                    data,
                    result
                )
            
            return result, 200
            
        except ValueError as e:
            return {'error': 'Valeurs numériques invalides'}, 400
        except Exception as e:
            logger.error(f"Erreur lors du calcul du plan d'épargne : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class LoanDurationCalculator(Resource):
    """Endpoint pour le calcul de la durée de remboursement"""
    
    def post(self):
        """Calculer la durée de remboursement d'un prêt sans intérêt"""
        try:
            data = request.get_json()
            
            loan_amount = data.get('loan_amount')
            monthly_payment = data.get('monthly_payment')
            
            if not loan_amount or not monthly_payment:
                return {'error': 'Le montant du prêt et le paiement mensuel sont requis'}, 400
            
            # Calculer la durée
            result = calculate_loan_duration(
                float(loan_amount),
                float(monthly_payment)
            )
            
            if result.get('error'):
                return {'error': result['error']}, 400
            
            # Sauvegarder le calcul si l'utilisateur est connecté
            user_id = get_jwt_identity() if request.headers.get('Authorization') else None
            if user_id:
                save_calculation(
                    user_id,
                    'loan_duration',
                    data,
                    result
                )
            
            return result, 200
            
        except ValueError as e:
            return {'error': 'Valeurs numériques invalides'}, 400
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la durée de prêt : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class BudgetSimulator(Resource):
    """Endpoint pour la simulation de budget"""
    
    def post(self):
        """Simuler un budget mensuel"""
        try:
            data = request.get_json()
            
            monthly_income = data.get('monthly_income')
            expenses = data.get('expenses', {})
            
            if not monthly_income:
                return {'error': 'Les revenus mensuels sont requis'}, 400
            
            if not isinstance(expenses, dict):
                return {'error': 'Les dépenses doivent être un objet'}, 400
            
            savings_goal = data.get('savings_goal')
            
            # Simuler le budget
            result = simulate_budget(
                float(monthly_income),
                {k: float(v) for k, v in expenses.items()},
                float(savings_goal) if savings_goal else None
            )
            
            if result.get('error'):
                return {'error': result['error']}, 400
            
            # Sauvegarder le calcul si l'utilisateur est connecté
            user_id = get_jwt_identity() if request.headers.get('Authorization') else None
            if user_id:
                save_calculation(
                    user_id,
                    'budget_simulation',
                    data,
                    result
                )
            
            return result, 200
            
        except ValueError as e:
            return {'error': 'Valeurs numériques invalides'}, 400
        except Exception as e:
            logger.error(f"Erreur lors de la simulation de budget : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class ZakatCalculator(Resource):
    """Endpoint pour le calcul de la Zakat"""
    
    def post(self):
        """Calculer la Zakat"""
        try:
            data = request.get_json()
            
            assets = data.get('assets')
            if not assets:
                return {'error': 'Le montant des actifs est requis'}, 400
            
            debts = data.get('debts', 0)
            nisab_value = data.get('nisab_value')
            
            # Calculer la Zakat
            result = calculate_zakat(
                float(assets),
                float(debts),
                float(nisab_value) if nisab_value else None
            )
            
            # Sauvegarder le calcul si l'utilisateur est connecté
            user_id = get_jwt_identity() if request.headers.get('Authorization') else None
            if user_id:
                save_calculation(
                    user_id,
                    'zakat_calculation',
                    data,
                    result
                )
            
            return result, 200
            
        except ValueError as e:
            return {'error': 'Valeurs numériques invalides'}, 400
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la Zakat : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class UserCalculations(Resource):
    """Endpoint pour récupérer l'historique des calculs"""
    
    @jwt_required()
    def get(self):
        """Récupérer les calculs de l'utilisateur connecté"""
        try:
            user_id = get_jwt_identity()
            
            # Paramètres de requête
            calculation_type = request.args.get('type')
            limit = request.args.get('limit', 10, type=int)
            limit = min(limit, 100)  # Limiter à 100 max
            
            # Récupérer les calculs
            calculations = get_user_calculations(
                user_id,
                calculation_type,
                limit
            )
            
            return {
                'calculations': [
                    {
                        'id': calc.id,
                        'type': calc.calculation_type,
                        'input': calc.input_data,
                        'result': calc.result_data,
                        'created_at': calc.created_at.isoformat()
                    }
                    for calc in calculations
                ]
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des calculs : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class FinancialTipsList(Resource):
    """Endpoint pour lister les conseils financiers"""
    
    def get(self):
        """Récupérer la liste des conseils financiers"""
        try:
            # Paramètres de requête
            category = request.args.get('category')
            limit = request.args.get('limit', 10, type=int)
            limit = min(limit, 50)  # Limiter à 50 max
            
            # Récupérer les conseils
            tips = get_financial_tips(category, limit)
            
            return {
                'tips': [tip.to_dict() for tip in tips],
                'total': len(tips)
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des conseils : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class FinancialTipDetail(Resource):
    """Endpoint pour un conseil financier spécifique"""
    
    def get(self, tip_id):
        """Récupérer un conseil financier par ID"""
        try:
            from model.finance_tips import FinancialTip
            
            tip = FinancialTip.query.get(tip_id)
            if not tip or not tip.is_published:
                return {'error': ERROR_MESSAGES['NOT_FOUND']}, 404
            
            # Incrémenter les vues
            increment_tip_views(tip_id)
            
            return tip.to_dict(), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du conseil : {str(e)}")
            return {'error': ERROR_MESSAGES['SERVER_ERROR']}, 500

class CalculatorInfo(Resource):
    """Endpoint pour obtenir les informations sur les calculatrices"""
    
    def get(self):
        """Obtenir les informations et limites des calculatrices"""
        from config.constant import HALAL_FINANCE, CURRENCIES
        
        return {
            'calculators': {
                'savings_plan': {
                    'name': "Plan d'épargne halal",
                    'description': "Calculez combien épargner mensuellement pour atteindre votre objectif",
                    'limits': {
                        'min_monthly_saving': HALAL_FINANCE['MIN_MONTHLY_SAVING'],
                        'max_duration_months': HALAL_FINANCE['MAX_LOAN_DURATION_MONTHS']
                    }
                },
                'loan_duration': {
                    'name': "Durée de remboursement",
                    'description': "Calculez la durée pour rembourser un prêt sans intérêt",
                    'limits': {
                        'min_loan_amount': HALAL_FINANCE['MIN_LOAN_AMOUNT'],
                        'max_loan_amount': HALAL_FINANCE['MAX_LOAN_AMOUNT'],
                        'max_duration_months': HALAL_FINANCE['MAX_LOAN_DURATION_MONTHS']
                    }
                },
                'budget_simulation': {
                    'name': "Simulation de budget",
                    'description': "Analysez vos revenus et dépenses pour optimiser votre épargne",
                    'expense_categories': [
                        'logement', 'alimentation', 'transport', 'santé',
                        'éducation', 'loisirs', 'autres'
                    ]
                },
                'zakat': {
                    'name': "Calcul de la Zakat",
                    'description': "Calculez votre Zakat annuelle (2.5% des actifs nets)",
                    'nisab_info': "Le Nisab est le seuil minimum de richesse pour être éligible"
                }
            },
            'currencies': CURRENCIES
        }, 200

# Fonction pour enregistrer toutes les routes des calculatrices
def register_tips_routes(api):
    """Enregistre toutes les routes des calculatrices et conseils"""
    api.add_resource(SavingsPlanCalculator, '/api/calculators/savings-plan')
    api.add_resource(LoanDurationCalculator, '/api/calculators/loan-duration')
    api.add_resource(BudgetSimulator, '/api/calculators/budget-simulation')
    api.add_resource(ZakatCalculator, '/api/calculators/zakat')
    api.add_resource(UserCalculations, '/api/calculators/history')
    api.add_resource(CalculatorInfo, '/api/calculators/info')
    api.add_resource(FinancialTipsList, '/api/tips')
    api.add_resource(FinancialTipDetail, '/api/tips/<int:tip_id>')