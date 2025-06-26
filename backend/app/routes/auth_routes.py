from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from datetime import datetime
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['firstName'],
            last_name=data['lastName'],
            country=data.get('country', 'DE'),
            newsletter=data.get('newsletter', False)
        )
        
        # Set password
        user.set_password(data['password'])
        
        # Set birth date if provided
        if 'birthDate' in data:
            user.birth_date = datetime.strptime(data['birthDate'], '%Y-%m-%d').date()
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'access_token': 'dummy-token'  # In production, use proper JWT
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        login_user(user, remember=data.get('rememberMe', False))
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'access_token': 'dummy-token'  # In production, use proper JWT
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    logout_user()
    return jsonify({'success': True})