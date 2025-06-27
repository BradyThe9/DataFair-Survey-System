#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Survey Routes for DataFair Survey System
Korrigiert: Optionaler Login-Schutz für API-Tests
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json

from ..database import db
from ..models import Survey, SurveyResponse, User

# Create Blueprint
surveys_bp = Blueprint('surveys', __name__)

@surveys_bp.route('/test', methods=['GET'])
def test_survey_system():
    """
    Test Survey System - Ohne Login-Schutz für Tests
    """
    try:
        survey_count = Survey.query.count()
        active_surveys = Survey.query.filter_by(is_active=True).count()
        
        return jsonify({
            'status': 'Survey system operational',
            'timestamp': datetime.utcnow().isoformat(),
            'total_surveys': survey_count,
            'active_surveys': active_surveys,
            'system_health': 'OK'
        })
    except Exception as e:
        print(f"Survey test error: {str(e)}")
        return jsonify({'error': 'Survey system test failed'}), 500

@surveys_bp.route('/available', methods=['GET'])
def get_available_surveys():
    """
    Get Available Surveys - Ohne Login-Schutz für API-Tests
    Für Produktion sollte @login_required aktiviert werden
    """
    try:
        # Optional: Check if user is logged in for personalized results
        user_id = current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None
        
        # Get active surveys
        surveys = Survey.query.filter_by(is_active=True).all()
        
        survey_list = []
        for survey in surveys:
            # Check if user has already completed this survey
            completed = False
            if user_id:
                existing_response = SurveyResponse.query.filter_by(
                    survey_id=survey.id,
                    user_id=user_id
                ).first()
                completed = existing_response is not None
            
            survey_data = {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'reward_amount': float(survey.reward_amount),
                'estimated_duration': survey.estimated_duration or 5,
                'total_responses': survey.total_responses,
                'max_responses': survey.max_responses,
                'completed_by_user': completed,
                'created_at': survey.created_at.isoformat()
            }
            
            # Only include questions count, not full questions for security
            if survey.questions:
                try:
                    questions = json.loads(survey.questions) if isinstance(survey.questions, str) else survey.questions
                    survey_data['question_count'] = len(questions)
                except:
                    survey_data['question_count'] = 0
            else:
                survey_data['question_count'] = 0
            
            survey_list.append(survey_data)
        
        return jsonify({
            'surveys': survey_list,
            'total_count': len(survey_list),
            'user_authenticated': user_id is not None
        })
        
    except Exception as e:
        print(f"Available surveys error: {str(e)}")
        return jsonify({'error': 'Failed to load available surveys'}), 500

@surveys_bp.route('/available-auth', methods=['GET'])
@login_required
def get_available_surveys_auth():
    """
    Get Available Surveys - Mit Login-Schutz
    """
    return get_available_surveys()

@surveys_bp.route('/<int:survey_id>', methods=['GET'])
def get_survey_details(survey_id):
    """
    Get Survey Details - Ohne Login für Public Preview
    """
    try:
        survey = Survey.query.get_or_404(survey_id)
        
        if not survey.is_active:
            return jsonify({'error': 'Survey is not active'}), 404
        
        # Parse questions
        questions = []
        if survey.questions:
            try:
                questions = json.loads(survey.questions) if isinstance(survey.questions, str) else survey.questions
            except:
                questions = []
        
        survey_data = {
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'questions': questions,
            'reward_amount': float(survey.reward_amount),
            'estimated_duration': survey.estimated_duration or 5,
            'max_responses': survey.max_responses,
            'total_responses': survey.total_responses,
            'created_at': survey.created_at.isoformat()
        }
        
        return jsonify(survey_data)
        
    except Exception as e:
        print(f"Survey details error: {str(e)}")
        return jsonify({'error': 'Survey not found'}), 404

@surveys_bp.route('/<int:survey_id>/start', methods=['POST'])
@login_required
def start_survey(survey_id):
    """
    Start Survey - Requires Authentication
    """
    try:
        survey = Survey.query.get_or_404(survey_id)
        
        if not survey.is_active:
            return jsonify({'error': 'Survey is not active'}), 400
        
        # Check if user already completed this survey
        existing_response = SurveyResponse.query.filter_by(
            survey_id=survey_id,
            user_id=current_user.id
        ).first()
        
        if existing_response:
            return jsonify({'error': 'You have already completed this survey'}), 400
        
        # Check if survey has reached max responses
        if survey.total_responses >= survey.max_responses:
            return jsonify({'error': 'Survey has reached maximum responses'}), 400
        
        # Create survey response entry
        response = SurveyResponse(
            survey_id=survey_id,
            user_id=current_user.id,
            started_at=datetime.utcnow(),
            is_completed=False
        )
        
        db.session.add(response)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Survey started successfully',
            'response_id': response.id,
            'survey': {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'reward_amount': float(survey.reward_amount)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Start survey error: {str(e)}")
        return jsonify({'error': 'Failed to start survey'}), 500

@surveys_bp.route('/<int:survey_id>/submit', methods=['POST'])
@login_required
def submit_survey(survey_id):
    """
    Submit Survey Response
    """
    try:
        data = request.get_json()
        
        if not data or 'responses' not in data:
            return jsonify({'error': 'Survey responses are required'}), 400
        
        # Find the survey response
        survey_response = SurveyResponse.query.filter_by(
            survey_id=survey_id,
            user_id=current_user.id,
            is_completed=False
        ).first()
        
        if not survey_response:
            return jsonify({'error': 'Survey not started or already completed'}), 400
        
        # Update survey response
        survey_response.responses = json.dumps(data['responses'])
        survey_response.completed_at = datetime.utcnow()
        survey_response.is_completed = True
        
        # Update survey total responses
        survey = Survey.query.get(survey_id)
        survey.total_responses += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Survey submitted successfully',
            'reward_amount': float(survey.reward_amount),
            'completion_time': survey_response.completed_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Submit survey error: {str(e)}")
        return jsonify({'error': 'Failed to submit survey'}), 500

@surveys_bp.route('/my-responses', methods=['GET'])
@login_required
def get_my_responses():
    """
    Get User's Survey Responses
    """
    try:
        responses = SurveyResponse.query.filter_by(
            user_id=current_user.id,
            is_completed=True
        ).all()
        
        response_list = []
        for response in responses:
            survey = Survey.query.get(response.survey_id)
            response_data = {
                'id': response.id,
                'survey': {
                    'id': survey.id,
                    'title': survey.title,
                    'reward_amount': float(survey.reward_amount)
                },
                'completed_at': response.completed_at.isoformat(),
                'started_at': response.started_at.isoformat()
            }
            response_list.append(response_data)
        
        return jsonify({
            'responses': response_list,
            'total_count': len(response_list)
        })
        
    except Exception as e:
        print(f"My responses error: {str(e)}")
        return jsonify({'error': 'Failed to load responses'}), 500

@surveys_bp.route('/stats', methods=['GET'])
def get_survey_stats():
    """
    Get Survey Statistics - Public endpoint
    """
    try:
        total_surveys = Survey.query.count()
        active_surveys = Survey.query.filter_by(is_active=True).count()
        total_responses = SurveyResponse.query.filter_by(is_completed=True).count()
        total_users = User.query.count()
        
        return jsonify({
            'total_surveys': total_surveys,
            'active_surveys': active_surveys,
            'total_responses': total_responses,
            'total_users': total_users,
            'updated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Survey stats error: {str(e)}")
        return jsonify({'error': 'Failed to load statistics'}), 500