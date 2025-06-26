from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app.database import db
from app.models import Earning, Payout, DataPermission, DataType, Activity

earning_bp = Blueprint('earning', __name__)

@earning_bp.route('/earnings', methods=['GET'])
@login_required
def get_earnings():
    """Get user's earnings overview"""
    try:
        # Current month earnings
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        this_month_earnings = db.session.query(func.sum(Earning.amount)).filter(
            Earning.user_id == current_user.id,
            extract('month', Earning.earned_at) == current_month,
            extract('year', Earning.earned_at) == current_year
        ).scalar() or 0.0
        
        # Total earnings
        total_earnings = db.session.query(func.sum(Earning.amount)).filter(
            Earning.user_id == current_user.id
        ).scalar() or 0.0
        
        # Available for payout (total minus already paid out AND pending)
        total_payouts = db.session.query(func.sum(Payout.amount)).filter(
            Payout.user_id == current_user.id,
            Payout.status.in_(['completed', 'processing', 'pending'])  # FIXED: Include pending
        ).scalar() or 0.0
        
        available_earnings = total_earnings - total_payouts
        
        # Pending payouts
        pending_payouts = db.session.query(func.sum(Payout.amount)).filter(
            Payout.user_id == current_user.id,
            Payout.status == 'pending'
        ).scalar() or 0.0
        
        # Monthly potential (from enabled data types)
        enabled_permissions = DataPermission.query.filter_by(
            user_id=current_user.id,
            enabled=True
        ).all()
        
        monthly_potential = sum(
            perm.data_type.monthly_value for perm in enabled_permissions 
            if perm.data_type
        )
        
        # Last 6 months for chart
        monthly_data = []
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_earnings = db.session.query(func.sum(Earning.amount)).filter(
                Earning.user_id == current_user.id,
                extract('month', Earning.earned_at) == month_date.month,
                extract('year', Earning.earned_at) == month_date.year
            ).scalar() or 0.0
            monthly_data.insert(0, month_earnings)
        
        return jsonify({
            'success': True,
            'earnings': {
                'thisMonth': this_month_earnings,
                'total': total_earnings,
                'available': max(0, available_earnings),  # Never negative
                'pending': pending_payouts,
                'monthlyPotential': monthly_potential,
                'monthlyData': monthly_data,
                'chartLabels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun']  # Simplified
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@earning_bp.route('/earnings/generate', methods=['POST'])
@login_required
def generate_monthly_earnings():
    """Generate monthly earnings for enabled data types (Admin/Cron function)"""
    try:
        # Get user's enabled data permissions
        enabled_permissions = DataPermission.query.filter_by(
            user_id=current_user.id,
            enabled=True
        ).all()
        
        total_generated = 0.0
        
        for permission in enabled_permissions:
            if permission.data_type:
                # Create earning entry
                earning = Earning(
                    user_id=current_user.id,
                    amount=permission.data_type.monthly_value,
                    source='data_share',
                    description=f'Monatliche Vergütung für {permission.data_type.name}'
                )
                db.session.add(earning)
                
                # Update last accessed
                permission.last_accessed = datetime.utcnow()
                
                total_generated += permission.data_type.monthly_value
                
                # Create activity
                activity = Activity(
                    user_id=current_user.id,
                    title='Daten genutzt',
                    description=f'Deine {permission.data_type.name}-Daten wurden von Unternehmen genutzt.',
                    activity_type='data_usage',
                    earning=permission.data_type.monthly_value,
                    company='Verschiedene Partner'
                )
                db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'€{total_generated:.2f} Verdienst generiert',
            'amount': total_generated
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@earning_bp.route('/payout', methods=['POST'])
@login_required
def request_payout():
    """Request a payout"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        amount = data.get('amount')
        method = data.get('method', 'paypal')
        
        # Validation
        if not amount:
            return jsonify({'error': 'Amount is required'}), 400
            
        try:
            amount = float(amount)
        except ValueError:
            return jsonify({'error': 'Invalid amount format'}), 400
            
        if amount < 10.0:
            return jsonify({'error': 'Minimum payout amount is €10.00'}), 400
            
        # Check available balance
        total_earnings = db.session.query(func.sum(Earning.amount)).filter(
            Earning.user_id == current_user.id
        ).scalar() or 0.0
        
        total_payouts = db.session.query(func.sum(Payout.amount)).filter(
            Payout.user_id == current_user.id,
            Payout.status.in_(['completed', 'processing', 'pending'])
        ).scalar() or 0.0
        
        available_balance = total_earnings - total_payouts
        
        if amount > available_balance:
            return jsonify({'error': f'Insufficient balance. Available: €{available_balance:.2f}'}), 400
            
        # Validate method
        valid_methods = ['paypal', 'bank', 'crypto']
        if method not in valid_methods:
            return jsonify({'error': 'Invalid payout method'}), 400
        
        # Create payout request
        payout = Payout(
            user_id=current_user.id,
            amount=amount,
            method=method,
            status='pending'
        )
        db.session.add(payout)
        
        # Create activity
        activity = Activity(
            user_id=current_user.id,
            title='Auszahlung beantragt',
            description=f'Du hast eine Auszahlung von €{amount:.2f} per {method.upper()} beantragt.',
            activity_type='payout_requested',
            earning=0.0,
            company='DataFair'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Auszahlung von €{amount:.2f} wurde beantragt',
            'payout': payout.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@earning_bp.route('/payouts', methods=['GET'])
@login_required
def get_payouts():
    """Get user's payout history"""
    try:
        payouts = Payout.query.filter_by(user_id=current_user.id)\
                              .order_by(Payout.requested_at.desc())\
                              .all()
        
        return jsonify({
            'success': True,
            'payouts': [payout.to_dict() for payout in payouts]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@earning_bp.route('/payouts/<int:payout_id>/status', methods=['PUT'])
@login_required  
def update_payout_status(payout_id):
    """Update payout status (Admin function)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        new_status = data.get('status')
        
        if new_status not in ['pending', 'processing', 'completed', 'failed']:
            return jsonify({'error': 'Invalid status'}), 400
            
        payout = Payout.query.filter_by(
            id=payout_id,
            user_id=current_user.id
        ).first()
        
        if not payout:
            return jsonify({'error': 'Payout not found'}), 404
            
        old_status = payout.status
        payout.status = new_status
        
        if new_status == 'completed':
            payout.completed_at = datetime.utcnow()
            
            # Create activity
            activity = Activity(
                user_id=current_user.id,
                title='Auszahlung abgeschlossen',
                description=f'Deine Auszahlung von €{payout.amount:.2f} wurde erfolgreich verarbeitet.',
                activity_type='payout_completed',
                earning=0.0,
                company='DataFair'
            )
            db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Payout status updated from {old_status} to {new_status}',
            'payout': payout.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@earning_bp.route('/earnings/bonus', methods=['POST'])
@login_required
def add_bonus_earning():
    """Add a bonus earning (Admin function or special promotions)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        amount = data.get('amount')
        description = data.get('description', 'Bonus')
        
        if not amount:
            return jsonify({'error': 'Amount is required'}), 400
            
        try:
            amount = float(amount)
        except ValueError:
            return jsonify({'error': 'Invalid amount format'}), 400
            
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        # Create bonus earning
        earning = Earning(
            user_id=current_user.id,
            amount=amount,
            source='bonus',
            description=description
        )
        db.session.add(earning)
        
        # Create activity
        activity = Activity(
            user_id=current_user.id,
            title='Bonus erhalten',
            description=description,
            activity_type='bonus',
            earning=amount,
            company='DataFair'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Bonus von €{amount:.2f} hinzugefügt',
            'earning': earning.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500