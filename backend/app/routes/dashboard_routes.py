# backend/app/routes/dashboard_routes.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app.database import db
from app.models import User, Earning, DataType, DataPermission

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
        
        # ECHTE Earnings Data aus der Datenbank
        earnings_data = get_user_earnings_data(current_user.id)
        
        # ECHTE DataTypes aus der Datenbank (ERSETZT HARDCODED!)
        data_types_list = get_user_data_types_with_permissions(current_user.id)
        
        # Activities mit echten Earnings
        activities_list = get_user_activities(current_user.id)
        
        # Statistics
        stats = {
            'totalDataTypes': len(data_types_list),
            'activeDataTypes': len([dt for dt in data_types_list if dt['enabled']]),
            'totalActivities': len(activities_list),
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
        print(f"Dashboard overview error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_user_earnings_data(user_id):
    """Get real earnings data from database"""
    try:
        # Total earnings
        total_earnings = db.session.query(func.sum(Earning.amount)).filter_by(
            user_id=user_id
        ).scalar() or 0.0
        
        # This month earnings
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_earnings = db.session.query(func.sum(Earning.amount)).filter(
            Earning.user_id == user_id,
            Earning.earned_at >= current_month
        ).scalar() or 0.0
        
        # Available for payout (assuming all earnings are available for now)
        available_earnings = total_earnings
        
        # Get last 6 months for chart
        monthly_data = []
        chart_labels = []
        
        for i in range(6):
            month_date = datetime.utcnow() - timedelta(days=30*i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if i == 0:
                # Current month - from start of month to now
                month_end = datetime.utcnow()
            else:
                # Previous months - full month
                if month_date.month == 12:
                    next_month = month_date.replace(year=month_date.year + 1, month=1)
                else:
                    next_month = month_date.replace(month=month_date.month + 1)
                month_end = next_month
            
            month_earnings = db.session.query(func.sum(Earning.amount)).filter(
                Earning.user_id == user_id,
                Earning.earned_at >= month_start,
                Earning.earned_at < month_end
            ).scalar() or 0.0
            
            monthly_data.insert(0, float(month_earnings))
            chart_labels.insert(0, month_date.strftime('%b'))
        
        return {
            'thisMonth': float(this_month_earnings),
            'total': float(total_earnings),
            'available': float(available_earnings),
            'pending': 0.0,
            'monthlyPotential': 57.00,
            'monthlyData': monthly_data,
            'chartLabels': chart_labels
        }
        
    except Exception as e:
        print(f"Error getting earnings data: {str(e)}")
        # Return default data on error
        return {
            'thisMonth': 0.0,
            'total': 0.0,
            'available': 0.0,
            'pending': 0.0,
            'monthlyPotential': 57.00,
            'monthlyData': [0, 0, 0, 0, 0, 0],
            'chartLabels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun']
        }

def get_user_data_types_with_permissions(user_id):
    """Get data types with user's permission status from DATABASE"""
    try:
        # Alle verfügbaren DataTypes aus DB laden
        all_data_types = DataType.query.filter_by(is_active=True).all()
        
        # User's permissions aus DB laden
        user_permissions = DataPermission.query.filter_by(user_id=user_id).all()
        permission_dict = {perm.data_type_id: perm for perm in user_permissions}
        
        # Kombiniere DataTypes mit Permission Status
        data_types_list = []
        for data_type in all_data_types:
            permission = permission_dict.get(data_type.id)
            
            data_type_info = {
                'id': data_type.id,
                'name': data_type.name,
                'description': data_type.description,
                'icon': data_type.icon,
                'monthlyValue': float(data_type.monthly_value),
                'category': data_type.category,
                'enabled': permission.enabled if permission else False,
                'grantedAt': permission.granted_at.isoformat() if permission and permission.granted_at else None,
                'lastAccessed': permission.last_accessed.isoformat() if permission and permission.last_accessed else None,
                'lastRequest': 'Nie' if not permission or not permission.last_accessed else permission.last_accessed.strftime('%d.%m.%Y')
            }
            
            data_types_list.append(data_type_info)
        
        return data_types_list
        
    except Exception as e:
        print(f"Error getting data types: {str(e)}")
        # Fallback zu leerem Array bei Fehler
        return []

def get_user_activities(user_id):
    """Get user activities from earnings"""
    try:
        # Get recent earnings as activities
        recent_earnings = Earning.query.filter_by(user_id=user_id)\
            .order_by(Earning.earned_at.desc())\
            .limit(10)\
            .all()
        
        activities = []
        for earning in recent_earnings:
            activities.append({
                'id': earning.id,
                'title': earning.description or 'Verdienst erhalten',
                'description': f'Du hast €{earning.amount:.2f} für {earning.source_type} erhalten.',
                'timestamp': earning.earned_at.strftime('%d.%m.%Y %H:%M'),
                'earning': float(earning.amount),
                'company': 'DataFair',
                'type': earning.source_type
            })
        
        # Add welcome message if no activities
        if not activities:
            activities.append({
                'id': 0,
                'title': 'Willkommen bei DataFair!',
                'description': 'Dein Account wurde erfolgreich erstellt. Aktiviere Datentypen um zu verdienen.',
                'timestamp': 'Gerade eben',
                'earning': 0.0,
                'company': 'DataFair',
                'type': 'welcome'
            })
        
        return activities
        
    except Exception as e:
        print(f"Error getting activities: {str(e)}")
        return [{
            'id': 0,
            'title': 'Willkommen bei DataFair!',
            'description': 'Dein Account wurde erfolgreich erstellt.',
            'timestamp': 'Gerade eben',
            'earning': 0.0,
            'company': 'DataFair',
            'type': 'welcome'
        }]

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
    """Generate REAL test earnings for demo purposes"""
    try:
        import random
        
        # Generate random test amount between 5 and 50 EUR
        test_amount = round(random.uniform(5.0, 50.0), 2)
        
        # Create real earning entry in database
        earning = Earning(
            user_id=current_user.id,
            amount=test_amount,
            source_type='test_data',
            description=f'Test-Verdienst generiert - Datennutzung simuliert',
            status='earned'
        )
        
        db.session.add(earning)
        db.session.commit()
        
        print(f"✅ Created test earning: €{test_amount} for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': f'€{test_amount:.2f} Test-Verdienst wurde deinem Guthaben hinzugefügt!',
            'amount': test_amount
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error generating test earnings: {str(e)}")
        return jsonify({'error': str(e)}), 500

def toggle_data_type_quick(data_type_id, enabled):
    """Quick toggle for data types from dashboard - JETZT MIT ECHTER DB"""
    try:
        # DataType aus DB laden
        data_type = DataType.query.get(data_type_id)
        if not data_type:
            return jsonify({'error': 'DataType nicht gefunden'}), 404
        
        # Prüfe ob User bereits eine Permission für diesen DataType hat
        permission = DataPermission.query.filter_by(
            user_id=current_user.id,
            data_type_id=data_type_id
        ).first()
        
        if not permission:
            # Erstelle neue Permission
            permission = DataPermission(
                user_id=current_user.id,
                data_type_id=data_type_id,
                enabled=enabled,
                granted_at=datetime.utcnow() if enabled else None
            )
            db.session.add(permission)
        else:
            # Update bestehende Permission
            permission.enabled = enabled
            permission.granted_at = datetime.utcnow() if enabled else permission.granted_at
            permission.updated_at = datetime.utcnow()
        
        # If enabling a data type, generate a small earning as reward
        if enabled:
            bonus_amount = 2.50
            earning = Earning(
                user_id=current_user.id,
                amount=bonus_amount,
                source_type='data_activation',
                description=f'Aktivierungsbonus für {data_type.name}',
                status='earned'
            )
            db.session.add(earning)
            
            message = f"'{data_type.name}' aktiviert! Du erhältst €{bonus_amount:.2f} Aktivierungsbonus."
        else:
            message = f"'{data_type.name}' deaktiviert"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'dataType': {
                'id': data_type.id,
                'enabled': enabled,
                'monthlyValue': float(data_type.monthly_value)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error toggling data type: {str(e)}")
        return jsonify({'error': str(e)}), 500

def quick_payout_request(amount, method='paypal'):
    """Quick payout request from dashboard"""
    try:
        if not amount or float(amount) < 10:
            return jsonify({'error': 'Mindestbetrag €10.00'}), 400
        
        # Check if user has enough balance
        total_earnings = db.session.query(func.sum(Earning.amount)).filter_by(
            user_id=current_user.id
        ).scalar() or 0.0
        
        if float(amount) > total_earnings:
            return jsonify({'error': 'Unzureichendes Guthaben'}), 400
            
        # For demo purposes, just return success
        # In production, this would create a payout request
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