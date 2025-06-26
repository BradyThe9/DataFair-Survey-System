from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.database import db
from app.models import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user's profile"""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user's profile"""
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'firstName' in data:
            if not data['firstName'].strip():
                return jsonify({'error': 'First name cannot be empty'}), 400
            current_user.first_name = data['firstName'].strip()
            
        if 'lastName' in data:
            if not data['lastName'].strip():
                return jsonify({'error': 'Last name cannot be empty'}), 400
            current_user.last_name = data['lastName'].strip()
            
        if 'email' in data:
            new_email = data['email'].strip()
            if not new_email:
                return jsonify({'error': 'Email cannot be empty'}), 400
                
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Email already taken by another user'}), 400
                
            current_user.email = new_email
            
        if 'birthDate' in data and data['birthDate']:
            try:
                # Parse birth date
                birth_date = datetime.strptime(data['birthDate'], '%Y-%m-%d').date()
                
                # Age validation (must be at least 16)
                today = datetime.now().date()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                
                if age < 16:
                    return jsonify({'error': 'You must be at least 16 years old'}), 400
                    
                current_user.birth_date = birth_date
            except ValueError:
                return jsonify({'error': 'Invalid birth date format. Use YYYY-MM-DD'}), 400
                
        if 'country' in data:
            # Basic country code validation (2 letters)
            country = data['country'].strip().upper()
            if len(country) == 2 and country.isalpha():
                current_user.country = country
            else:
                return jsonify({'error': 'Invalid country code'}), 400
                
        if 'newsletter' in data:
            current_user.newsletter = bool(data['newsletter'])
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile/password', methods=['PUT'])
@login_required
def change_password():
    """Change user's password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password required'}), 400
            
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
            
        # Validate new password
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters long'}), 400
            
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile/delete', methods=['DELETE'])
@login_required
def delete_account():
    """Delete user account (GDPR compliance)"""
    try:
        data = request.get_json()
        password = data.get('password') if data else None
        
        if not password:
            return jsonify({'error': 'Password required to delete account'}), 400
            
        # Verify password
        if not current_user.check_password(password):
            return jsonify({'error': 'Incorrect password'}), 400
            
        # In a real app, you might want to:
        # 1. Anonymize data instead of deleting
        # 2. Keep some records for legal/accounting purposes
        # 3. Send confirmation email
        
        user_id = current_user.id
        db.session.delete(current_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500