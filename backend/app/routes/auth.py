#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Routes for DataFair Survey System
Korrigierte Flask-Login Integration
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import re
from datetime import datetime

from ..database import db
from ..models import User

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Passwort muss mindestens 6 Zeichen lang sein"
    return True, "OK"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User Login Endpoint
    GET: Return login status
    POST: Authenticate user
    """
    if request.method == 'GET':
        # Return current login status
        if current_user.is_authenticated:
            return jsonify({
                'logged_in': True,
                'user': {
                    'id': current_user.id,
                    'email': current_user.email,
                    'first_name': current_user.first_name,
                    'last_name': current_user.last_name
                }
            })
        else:
            return jsonify({'logged_in': False})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            # Validation
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            if not validate_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Find user
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Check password
            if not check_password_hash(user.password_hash, password):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Check if user is verified
            if not user.is_verified:
                return jsonify({'error': 'Please verify your email address first'}), 401
            
            # Login user
            login_user(user, remember=True)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            })
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User Logout"""
    try:
        logout_user()
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User Registration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract data
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        # Validation
        if not all([email, password, first_name, last_name]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid, password_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': password_msg}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create new user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            is_verified=True  # Auto-verify for demo purposes
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get User Profile"""
    try:
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'created_at': current_user.created_at.isoformat(),
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                'is_verified': current_user.is_verified
            }
        })
    except Exception as e:
        print(f"Profile error: {str(e)}")
        return jsonify({'error': 'Failed to load profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update User Profile"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'first_name' in data:
            current_user.first_name = data['first_name'].strip()
        
        if 'last_name' in data:
            current_user.last_name = data['last_name'].strip()
        
        # Password change
        if 'current_password' in data and 'new_password' in data:
            if not check_password_hash(current_user.password_hash, data['current_password']):
                return jsonify({'error': 'Current password is incorrect'}), 400
            
            is_valid, password_msg = validate_password(data['new_password'])
            if not is_valid:
                return jsonify({'error': password_msg}), 400
            
            current_user.password_hash = generate_password_hash(data['new_password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Profile update failed'}), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check Authentication Status"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name
            }
        })
    else:
        return jsonify({'authenticated': False})