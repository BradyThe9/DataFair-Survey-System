#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General API Routes for DataFair Survey System
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json

from ..database import db
from ..models import User, Survey, SurveyResponse

# Create Blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def api_info():
    """API Information"""
    return jsonify({
        'name': 'DataFair Survey System API',
        'version': '1.0.0',
        'description': 'API for fair data compensation and surveys',
        'endpoints': {
            'auth': {
                'login': 'POST /auth/login',
                'logout': 'POST /auth/logout',
                'register': 'POST /auth/register',
                'profile': 'GET/PUT /auth/profile'
            },
            'surveys': {
                'available': 'GET /api/surveys/available',
                'details': 'GET /api/surveys/{id}',
                'start': 'POST /api/surveys/{id}/start',
                'submit': 'POST /api/surveys/{id}/submit',
                'my_responses': 'GET /api/surveys/my-responses'
            },
            'users': {
                'profile': 'GET /api/profile',
                'earnings': 'GET /api/earnings',
                'payouts': 'GET /api/payouts'
            }
        }
    })

@api_bp.route('/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get Complete User Profile with Statistics"""
    try:
        # Get user's survey responses
        completed_surveys = SurveyResponse.query.filter_by(
            user_id=current_user.id,
            is_completed=True
        ).count()
        
        # Calculate earnings
        earnings_query = db.session.query(
            db.func.sum(Survey.reward_amount)
        ).join(SurveyResponse).filter(
            SurveyResponse.user_id == current_user.id,
            SurveyResponse.is_completed == True
        ).scalar()
        
        total_earnings = float(earnings_query or 0)
        
        # Get recent survey activity
        recent_responses = SurveyResponse.query.filter_by(
            user_id=current_user.id,
            is_completed=True
        ).order_by(SurveyResponse.completed_at.desc()).limit(5).all()
        
        recent_activity = []
        for response in recent_responses:
            survey = Survey.query.get(response.survey_id)
            recent_activity.append({
                'survey_title': survey.title,
                'completed_at': response.completed_at.isoformat(),
                'reward': float(survey.reward_amount)
            })
        
        profile_data = {
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'created_at': current_user.created_at.isoformat(),
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                'is_verified': current_user.is_verified
            },
            'statistics': {
                'completed_surveys': completed_surveys,
                'total_earnings': total_earnings,
                'recent_activity': recent_activity
            }
        }
        
        return jsonify(profile_data)
        
    except Exception as e:
        print(f"Profile API error: {str(e)}")
        return jsonify({'error': 'Failed to load profile'}), 500

@api_bp.route('/earnings', methods=['GET'])
@login_required
def get_earnings():
    """Get User's Earnings Information"""
    try:
        # Get all completed survey responses with earnings
        responses = db.session.query(
            SurveyResponse, Survey
        ).join(Survey).filter(
            SurveyResponse.user_id == current_user.id,
            SurveyResponse.is_completed == True
        ).order_by(SurveyResponse.completed_at.desc()).all()
        
        earnings_list = []
        total_earnings = 0
        
        for response, survey in responses:
            earning = {
                'id': response.id,
                'survey_title': survey.title,
                'amount': float(survey.reward_amount),
                'completed_at': response.completed_at.isoformat(),
                'status': 'earned'
            }
            earnings_list.append(earning)
            total_earnings += survey.reward_amount
        
        # Calculate this month's earnings
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_earnings = sum([
            survey.reward_amount for response, survey in responses
            if response.completed_at >= current_month
        ])
        
        return jsonify({
            'total_earnings': float(total_earnings),
            'monthly_earnings': float(monthly_earnings),
            'pending_payout': float(total_earnings),  # Simplified - all earnings pending
            'earnings_history': earnings_list,
            'currency': 'EUR'
        })
        
    except Exception as e:
        print(f"Earnings API error: {str(e)}")
        return jsonify({'error': 'Failed to load earnings'}), 500

@api_bp.route('/payouts', methods=['GET'])
@login_required
def get_payouts():
    """Get User's Payout History"""
    try:
        # For demo purposes, return empty payout history
        # In production, this would query a payouts table
        return jsonify({
            'payouts': [],
            'total_paid': 0.0,
            'pending_amount': 0.0,
            'next_payout_date': None,
            'payout_methods': ['PayPal', 'Bank Transfer', 'Cryptocurrency']
        })
        
    except Exception as e:
        print(f"Payouts API error: {str(e)}")
        return jsonify({'error': 'Failed to load payouts'}), 500

@api_bp.route('/payout', methods=['POST'])
@login_required
def request_payout():
    """Request a Payout"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        amount = data.get('amount')
        method = data.get('method')
        
        if not amount or not method:
            return jsonify({'error': 'Amount and method are required'}), 400
        
        # Calculate available balance
        earnings_query = db.session.query(
            db.func.sum(Survey.reward_amount)
        ).join(SurveyResponse).filter(
            SurveyResponse.user_id == current_user.id,
            SurveyResponse.is_completed == True
        ).scalar()
        
        available_balance = float(earnings_query or 0)
        
        if amount > available_balance:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # For demo purposes, just return success
        # In production, this would create a payout request
        return jsonify({
            'success': True,
            'message': 'Payout request submitted successfully',
            'payout_id': f"PO_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'amount': amount,
            'method': method,
            'estimated_processing_time': '3-5 business days'
        })
        
    except Exception as e:
        print(f"Payout request error: {str(e)}")
        return jsonify({'error': 'Failed to process payout request'}), 500

@api_bp.route('/data-types', methods=['GET'])
def get_data_types():
    """Get Available Data Types for Permission Management"""
    try:
        data_types = [
            {
                'id': 'browsing_history',
                'name': 'Browsing History',
                'description': 'Websites you visit and time spent',
                'value_per_month': 5.50,
                'privacy_level': 'medium'
            },
            {
                'id': 'location_data',
                'name': 'Location Data',
                'description': 'GPS location and movement patterns',
                'value_per_month': 8.25,
                'privacy_level': 'high'
            },
            {
                'id': 'shopping_behavior',
                'name': 'Shopping Behavior',
                'description': 'Purchase history and preferences',
                'value_per_month': 6.75,
                'privacy_level': 'medium'
            },
            {
                'id': 'social_media',
                'name': 'Social Media Activity',
                'description': 'Posts, likes, and interactions',
                'value_per_month': 4.00,
                'privacy_level': 'low'
            },
            {
                'id': 'search_queries',
                'name': 'Search Queries',
                'description': 'Search terms and clicked results',
                'value_per_month': 3.25,
                'privacy_level': 'medium'
            }
        ]
        
        return jsonify({
            'data_types': data_types,
            'total_types': len(data_types),
            'currency': 'EUR'
        })
        
    except Exception as e:
        print(f"Data types error: {str(e)}")
        return jsonify({'error': 'Failed to load data types'}), 500

@api_bp.route('/data-permissions', methods=['GET', 'POST'])
@login_required
def manage_data_permissions():
    """Manage User's Data Permissions"""
    try:
        if request.method == 'GET':
            # For demo purposes, return default permissions
            # In production, this would query user's actual permissions
            permissions = [
                {
                    'data_type': 'browsing_history',
                    'enabled': False,
                    'monthly_value': 5.50
                },
                {
                    'data_type': 'location_data',
                    'enabled': False,
                    'monthly_value': 8.25
                },
                {
                    'data_type': 'shopping_behavior',
                    'enabled': True,
                    'monthly_value': 6.75
                },
                {
                    'data_type': 'social_media',
                    'enabled': True,
                    'monthly_value': 4.00
                },
                {
                    'data_type': 'search_queries',
                    'enabled': False,
                    'monthly_value': 3.25
                }
            ]
            
            return jsonify({
                'permissions': permissions,
                'updated_at': datetime.utcnow().isoformat()
            })
            
        elif request.method == 'POST':
            data = request.get_json()
            
            if not data or 'permissions' not in data:
                return jsonify({'error': 'Permissions data required'}), 400
            
            # For demo purposes, just return success
            # In production, this would update user's permissions in database
            return jsonify({
                'success': True,
                'message': 'Data permissions updated successfully',
                'updated_at': datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        print(f"Data permissions error: {str(e)}")
        return jsonify({'error': 'Failed to manage data permissions'}), 500