# backend/app/routes/dashboard_routes.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app.database import db
from app.models import User

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/overview', methods=['GET'])
@login_required
def get_dashboard_overview():
    """Get complete dashboard overview data in one call"""
    try:
        # User Profile
        user_data = {
            'id': current_user.id,
            'email': current_user.email,
            'firstName': current_user.first_name,
            'lastName': current_user.last_name,
            'joinDate': current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else datetime.utcnow().isoformat()
        }
        
        # Mock Data Types (da wir noch keine DataType Tabelle haben)
        data_types_list = [
            {
                'id': 1,
                'name': 'Shopping-Verhalten',
                'description': 'Online-Einkäufe, besuchte Shops, Produktinteressen',
                'icon': '🛒',
                'monthlyValue': 12.00,
                'category': 'E-Commerce',
                'enabled': False,
                'grantedAt': None,
                'lastAccessed': None,
                'lastRequest': 'Nie'
            },
            {
                'id': 2,
                'name': 'Demografische Daten',
                'description': 'Alter, Geschlecht, Wohnort, Familienstand',
                'icon': '👤',
                'monthlyValue': 8.50,
                'category': 'Persönlich',
                'enabled': False,
                'grantedAt': None,
                'lastAccessed': None,
                'lastRequest': 'Nie'
            },
            {
                'id': 3,
                'name': 'Interessensbereiche',
                'description': 'Hobbys, Sport, Reisen, Entertainment-Präferenzen',
                'icon': '🎯',
                'monthlyValue': 6.75,
                'category': 'Lifestyle',
                'enabled': False,
                'grantedAt': None,
                'lastAccessed': None,
                'lastRequest': 'Nie'
            },
            {
                'id': 4,
                'name': 'Technologie-Nutzung',
                'description': 'Geräte, Apps, Software-Präferenzen',
                'icon': '📱',
                'monthlyValue': 5.25,
                'category': 'Technologie',
                'enabled': False,
                'grantedAt': None,
                'lastAccessed': None,
                'lastRequest': 'Nie'
            },
            {
                'id': 5,
                'name': 'Fitness & Gesundheit',
                'description': 'Aktivitätsdaten, Gesundheitsinteressen (anonymisiert)',
                'icon': '💪',
                'monthlyValue': 9.00,
                'category': 'Gesundheit',
                'enabled': False,
                'grantedAt': None,
                'lastAccessed': None,
                'lastRequest': 'Nie'
            },
            {
                'id': 6,
                'name': 'Finanzverhalten',
                'description': 'Ausgabenkategorien, Spar- und Investitionsinteressen',
                'icon': '💰',
                'monthlyValue': 15.50,
                'category': 'Finanzen',
                'enabled': False,
                'grantedAt': None,
                'lastAccessed': None,
                'lastRequest': 'Nie'
            }
        ]
        
        # Mock Earnings Data
        earnings_data = {
            'thisMonth': 0.0,
            'total': 0.0,
            'available': 0.0,
            'pending': 0.0,
            'monthlyPotential': 57.00,  # Sum of all data types
            'monthlyData': [0, 0, 0, 0, 0, 0],
            'chartLabels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun']
        }
        
        # Mock Activities
        activities_list = [
            {
                'id': 1,
                'title': 'Willkommen bei DataFair!',
                'description': 'Dein Account wurde erfolgreich erstellt. Aktiviere Datentypen um zu verdienen.',
                'timestamp': 'Gerade eben',
                'earning': 0.0,
                'company': 'DataFair',
                'type': 'welcome'
            }
        ]
        
        # Statistics
        stats = {
            'totalDataTypes': len(data_types_list),
            'activeDataTypes': 0,
            'totalActivities': 1,
            'memberSince': datetime.utcnow().strftime('%B %Y')
        }
        
        return jsonify({
            'success': True,
            'dashboard': {
                'user': user_data,
                'earnings': earnings_data,
                'dataTypes': data_types_list,
                'activities': activities_list,
                'stats': stats,
                'notifications': {
                    'unread': 0,
                    'hasNewSurveys': False
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/quick-actions', methods=['POST'])
@login_required  
def handle_quick_action():
    """Handle quick actions from dashboard"""
    try:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'generate_test_earnings':
            return generate_test_earnings()
        elif action == 'toggle_data_type':
            return toggle_data_type_quick(data.get('dataTypeId'), data.get('enabled'))
        elif action == 'request_payout':
            return quick_payout_request(data.get('amount'), data.get('method'))
        else:
            return jsonify({'error': 'Unknown action'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_test_earnings():
    """Generate test earnings for demo purposes"""
    try:
        # Mock test earnings generation
        test_amount = 25.50
        
        return jsonify({
            'success': True,
            'message': f'€{test_amount:.2f} Test-Verdienst generiert! (Demo-Modus)',
            'amount': test_amount
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def toggle_data_type_quick(data_type_id, enabled):
    """Quick toggle for data types from dashboard"""
    try:
        # Mock data type names
        data_type_names = {
            1: 'Shopping-Verhalten',
            2: 'Demografische Daten', 
            3: 'Interessensbereiche',
            4: 'Technologie-Nutzung',
            5: 'Fitness & Gesundheit',
            6: 'Finanzverhalten'
        }
        
        data_type_name = data_type_names.get(data_type_id, 'Unbekannter Datentyp')
        
        return jsonify({
            'success': True,
            'message': f"'{data_type_name}' {'aktiviert' if enabled else 'deaktiviert'} (Demo-Modus)",
            'dataType': {
                'id': data_type_id,
                'enabled': enabled,
                'monthlyValue': 12.00
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def quick_payout_request(amount, method='paypal'):
    """Quick payout request from dashboard"""
    try:
        if not amount or float(amount) < 10:
            return jsonify({'error': 'Mindestbetrag €10.00'}), 400
            
        return jsonify({
            'success': True,
            'message': f'Auszahlung von €{amount} per {method.upper()} beantragt (Demo-Modus)',
            'payout': {
                'id': 1,
                'amount': float(amount),
                'method': method,
                'status': 'pending',
                'date': datetime.utcnow().strftime('%d.%m.%Y')
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500