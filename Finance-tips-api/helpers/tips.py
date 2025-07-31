"""
Helper functions pour les calculs financiers halal et les conseils
"""
from datetime import datetime, timedelta
from config.constant import HALAL_FINANCE, CURRENCIES
from config.db import db
from model.finance_tips import Calculation, FinancialTip
import math
import json

def validate_amount(amount, min_amount=None, max_amount=None):
    """
    Valide un montant
    Retourne (valid, error_message)
    """
    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Le montant doit être positif"
        
        if min_amount and amount < min_amount:
            return False, f"Le montant minimum est {min_amount}"
        
        if max_amount and amount > max_amount:
            return False, f"Le montant maximum est {max_amount}"
        
        return True, None
    except (ValueError, TypeError):
        return False, "Montant invalide"

def validate_duration(months):
    """
    Valide une durée en mois
    Retourne (valid, error_message)
    """
    try:
        months = int(months)
        if months <= 0:
            return False, "La durée doit être positive"
        
        if months > HALAL_FINANCE['MAX_LOAN_DURATION_MONTHS']:
            return False, f"La durée maximum est {HALAL_FINANCE['MAX_LOAN_DURATION_MONTHS']} mois"
        
        return True, None
    except (ValueError, TypeError):
        return False, "Durée invalide"

def calculate_savings_plan(target_amount, monthly_saving=None, duration_months=None):
    """
    Calcule un plan d'épargne halal (sans intérêts)
    
    Paramètres:
    - target_amount: Montant cible à atteindre
    - monthly_saving: Épargne mensuelle (si fourni, calcule la durée)
    - duration_months: Durée en mois (si fourni, calcule l'épargne mensuelle)
    
    Retourne: dict avec les résultats du calcul
    """
    result = {
        'calculation_type': 'savings_plan',
        'target_amount': target_amount,
        'currency': 'EUR',
        'error': None
    }
    
    # Validation du montant cible
    valid, error = validate_amount(target_amount, min_amount=HALAL_FINANCE['MIN_MONTHLY_SAVING'])
    if not valid:
        result['error'] = error
        return result
    
    # Cas 1: On a l'épargne mensuelle, on calcule la durée
    if monthly_saving is not None:
        valid, error = validate_amount(monthly_saving, min_amount=HALAL_FINANCE['MIN_MONTHLY_SAVING'])
        if not valid:
            result['error'] = error
            return result
        
        duration_months = math.ceil(target_amount / monthly_saving)
        result.update({
            'monthly_saving': monthly_saving,
            'duration_months': duration_months,
            'duration_years': round(duration_months / 12, 1),
            'total_saved': monthly_saving * duration_months
        })
    
    # Cas 2: On a la durée, on calcule l'épargne mensuelle
    elif duration_months is not None:
        valid, error = validate_duration(duration_months)
        if not valid:
            result['error'] = error
            return result
        
        monthly_saving = math.ceil(target_amount / duration_months)
        result.update({
            'monthly_saving': monthly_saving,
            'duration_months': duration_months,
            'duration_years': round(duration_months / 12, 1),
            'total_saved': monthly_saving * duration_months
        })
    
    else:
        result['error'] = "Veuillez fournir soit l'épargne mensuelle, soit la durée"
        return result
    
    # Ajouter des suggestions
    result['suggestions'] = generate_savings_suggestions(target_amount, monthly_saving, duration_months)
    
    return result

def calculate_loan_duration(loan_amount, monthly_payment):
    """
    Calcule la durée de remboursement d'un prêt sans intérêt
    
    Paramètres:
    - loan_amount: Montant du prêt
    - monthly_payment: Paiement mensuel
    
    Retourne: dict avec les résultats
    """
    result = {
        'calculation_type': 'loan_duration',
        'loan_amount': loan_amount,
        'monthly_payment': monthly_payment,
        'currency': 'EUR',
        'error': None
    }
    
    # Validation du montant du prêt
    valid, error = validate_amount(
        loan_amount, 
        min_amount=HALAL_FINANCE['MIN_LOAN_AMOUNT'],
        max_amount=HALAL_FINANCE['MAX_LOAN_AMOUNT']
    )
    if not valid:
        result['error'] = error
        return result
    
    # Validation du paiement mensuel
    valid, error = validate_amount(monthly_payment, min_amount=1)
    if not valid:
        result['error'] = error
        return result
    
    if monthly_payment > loan_amount:
        result['error'] = "Le paiement mensuel ne peut pas dépasser le montant du prêt"
        return result
    
    # Calcul de la durée
    duration_months = math.ceil(loan_amount / monthly_payment)
    
    # Vérification de la durée maximum
    if duration_months > HALAL_FINANCE['MAX_LOAN_DURATION_MONTHS']:
        result['error'] = f"La durée de remboursement dépasse le maximum autorisé ({HALAL_FINANCE['MAX_LOAN_DURATION_MONTHS']} mois)"
        return result
    
    result.update({
        'duration_months': duration_months,
        'duration_years': round(duration_months / 12, 1),
        'total_paid': monthly_payment * duration_months,
        'last_payment': loan_amount - (monthly_payment * (duration_months - 1))
    })
    
    # Générer un échéancier
    result['payment_schedule'] = generate_payment_schedule(loan_amount, monthly_payment, duration_months)
    
    return result

def simulate_budget(monthly_income, expenses, savings_goal=None):
    """
    Simule un budget mensuel
    
    Paramètres:
    - monthly_income: Revenus mensuels
    - expenses: Dict des dépenses par catégorie
    - savings_goal: Objectif d'épargne mensuel (optionnel)
    
    Retourne: dict avec l'analyse du budget
    """
    result = {
        'calculation_type': 'budget_simulation',
        'monthly_income': monthly_income,
        'currency': 'EUR',
        'error': None
    }
    
    # Validation des revenus
    valid, error = validate_amount(monthly_income, min_amount=0)
    if not valid:
        result['error'] = error
        return result
    
    # Calcul des dépenses totales
    total_expenses = 0
    expense_breakdown = {}
    
    for category, amount in expenses.items():
        valid, error = validate_amount(amount, min_amount=0)
        if not valid:
            result['error'] = f"Dépense invalide pour {category}: {error}"
            return result
        
        total_expenses += amount
        expense_breakdown[category] = {
            'amount': amount,
            'percentage': round((amount / monthly_income * 100) if monthly_income > 0 else 0, 1)
        }
    
    # Calcul de l'épargne disponible
    available_savings = monthly_income - total_expenses
    
    result.update({
        'total_expenses': total_expenses,
        'expense_breakdown': expense_breakdown,
        'available_savings': available_savings,
        'savings_rate': round((available_savings / monthly_income * 100) if monthly_income > 0 else 0, 1),
        'budget_status': 'excédentaire' if available_savings > 0 else ('équilibré' if available_savings == 0 else 'déficitaire')
    })
    
    # Analyse par rapport à l'objectif d'épargne
    if savings_goal is not None:
        valid, error = validate_amount(savings_goal, min_amount=0)
        if valid:
            result['savings_goal'] = savings_goal
            result['goal_achievable'] = available_savings >= savings_goal
            result['goal_gap'] = savings_goal - available_savings if not result['goal_achievable'] else 0
    
    # Recommandations
    result['recommendations'] = generate_budget_recommendations(
        monthly_income, total_expenses, available_savings, expense_breakdown
    )
    
    return result

def generate_savings_suggestions(target_amount, monthly_saving, duration_months):
    """Génère des suggestions pour le plan d'épargne"""
    suggestions = []
    
    # Suggestion pour atteindre l'objectif plus rapidement
    if duration_months > 12:
        faster_saving = math.ceil(target_amount / 12)
        suggestions.append({
            'type': 'faster',
            'description': f"En épargnant {faster_saving}€ par mois, vous atteindrez votre objectif en 1 an"
        })
    
    # Suggestion pour une épargne plus confortable
    if monthly_saving > target_amount * 0.1:  # Si l'épargne mensuelle > 10% de l'objectif
        comfortable_duration = math.ceil(target_amount / (target_amount * 0.05))
        comfortable_saving = math.ceil(target_amount / comfortable_duration)
        suggestions.append({
            'type': 'comfortable',
            'description': f"Une épargne de {comfortable_saving}€ par mois sur {comfortable_duration} mois pourrait être plus confortable"
        })
    
    return suggestions

def generate_payment_schedule(loan_amount, monthly_payment, duration_months):
    """Génère un échéancier de remboursement"""
    schedule = []
    remaining_balance = loan_amount
    
    for month in range(1, duration_months + 1):
        payment = min(monthly_payment, remaining_balance)
        remaining_balance -= payment
        
        schedule.append({
            'month': month,
            'payment': payment,
            'remaining_balance': remaining_balance,
            'cumulative_paid': loan_amount - remaining_balance
        })
        
        if remaining_balance <= 0:
            break
    
    return schedule[:12]  # Retourner seulement les 12 premiers mois

def generate_budget_recommendations(income, expenses, savings, expense_breakdown):
    """Génère des recommandations pour le budget"""
    recommendations = []
    
    # Recommandation sur le taux d'épargne
    savings_rate = (savings / income * 100) if income > 0 else 0
    
    if savings_rate < 10:
        recommendations.append({
            'type': 'savings',
            'priority': 'high',
            'description': "Votre taux d'épargne est faible. Essayez d'atteindre au moins 10% de vos revenus"
        })
    elif savings_rate >= 20:
        recommendations.append({
            'type': 'savings',
            'priority': 'info',
            'description': "Excellent taux d'épargne! Vous épargnez plus de 20% de vos revenus"
        })
    
    # Analyse des dépenses par catégorie
    for category, data in expense_breakdown.items():
        percentage = data['percentage']
        
        # Recommandations basées sur des ratios standards
        if category.lower() == 'logement' and percentage > 35:
            recommendations.append({
                'type': 'expense',
                'priority': 'medium',
                'category': category,
                'description': f"Vos dépenses de {category} représentent {percentage}% de vos revenus. L'idéal est de rester sous 35%"
            })
        
        elif category.lower() in ['alimentation', 'nourriture'] and percentage > 15:
            recommendations.append({
                'type': 'expense',
                'priority': 'low',
                'category': category,
                'description': f"Vos dépenses d'{category} semblent élevées ({percentage}%). Cherchez des moyens de réduire"
            })
    
    # Recommandation si budget déficitaire
    if savings < 0:
        recommendations.append({
            'type': 'budget',
            'priority': 'critical',
            'description': f"Attention! Votre budget est déficitaire de {abs(savings)}€. Réduisez vos dépenses ou augmentez vos revenus"
        })
    
    return recommendations

def save_calculation(user_id, calculation_type, input_data, result_data):
    """Sauvegarde un calcul en base de données"""
    try:
        calculation = Calculation(
            user_id=user_id,
            calculation_type=calculation_type,
            input_data=input_data,
            result_data=result_data
        )
        
        db.session.add(calculation)
        db.session.commit()
        
        return calculation
    except Exception as e:
        db.session.rollback()
        return None

def get_user_calculations(user_id, calculation_type=None, limit=10):
    """Récupère les calculs d'un utilisateur"""
    query = Calculation.query.filter_by(user_id=user_id)
    
    if calculation_type:
        query = query.filter_by(calculation_type=calculation_type)
    
    return query.order_by(Calculation.created_at.desc()).limit(limit).all()

def get_financial_tips(category=None, limit=10, only_published=True):
    """Récupère les conseils financiers"""
    query = FinancialTip.query
    
    if only_published:
        query = query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    
    return query.order_by(FinancialTip.published_at.desc()).limit(limit).all()

def increment_tip_views(tip_id):
    """Incrémente le compteur de vues d'un conseil"""
    tip = FinancialTip.query.get(tip_id)
    if tip:
        tip.views_count += 1
        db.session.commit()
        return True
    return False

def format_currency(amount, currency='EUR'):
    """Formate un montant avec la devise"""
    currency_info = CURRENCIES.get(currency, CURRENCIES['EUR'])
    return f"{amount:,.2f} {currency_info['symbol']}"

def calculate_zakat(assets, debts=0, nisab_value=None):
    """
    Calcule la Zakat (aumône obligatoire en Islam)
    2.5% des actifs nets si au-dessus du Nisab
    """
    net_assets = assets - debts
    
    # Nisab par défaut (équivalent à 85g d'or, à ajuster)
    if nisab_value is None:
        nisab_value = 3000  # Valeur approximative en EUR
    
    if net_assets >= nisab_value:
        zakat_amount = net_assets * 0.025  # 2.5%
        return {
            'eligible': True,
            'net_assets': net_assets,
            'zakat_amount': zakat_amount,
            'nisab_value': nisab_value
        }
    else:
        return {
            'eligible': False,
            'net_assets': net_assets,
            'nisab_value': nisab_value,
            'shortfall': nisab_value - net_assets
        }