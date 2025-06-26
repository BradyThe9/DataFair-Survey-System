# backend/app/routes/surveys.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app.models import Survey, SurveyResponse, SURVEY_CATEGORIES
from app.database import db

surveys_bp = Blueprint('surveys', __name__, url_prefix='/api/surveys')

@surveys_bp.route('/test', methods=['GET'])
def test_surveys():
    """Test endpoint"""
    return jsonify({
        'success': True,
        'message': 'Survey system is working!',
        'timestamp': datetime.utcnow().isoformat()
    })

@surveys_bp.route('/available', methods=['GET'])
@login_required
def get_available_surveys():
    """Get all available surveys for the current user"""
    try:
        user_id = current_user.id
        
        # Get all active surveys that user hasn't participated in yet
        available_surveys = db.session.query(Survey).filter(
            and_(
                Survey.status == 'active',
                or_(Survey.expires_at.is_(None), Survey.expires_at > datetime.utcnow()),
                ~Survey.id.in_(
                    db.session.query(SurveyResponse.survey_id).filter(
                        SurveyResponse.user_id == user_id
                    )
                )
            )
        ).all()
        
        # Convert to dict
        result = []
        for survey in available_surveys:
            survey_data = survey.to_dict()
            survey_data['category_display'] = SURVEY_CATEGORIES.get(survey.category, survey.category)
            survey_data['slots_remaining'] = survey.get_slots_remaining()
            result.append(survey_data)
        
        return jsonify({
            'success': True,
            'surveys': result,
            'total_potential_earnings': sum(s['base_reward'] for s in result),
            'count': len(result)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching available surveys: {str(e)}")
        return jsonify({'success': False, 'message': f'Fehler beim Laden der Umfragen: {str(e)}'}), 500

@surveys_bp.route('/<int:survey_id>', methods=['GET'])
@login_required
def get_survey_details(survey_id):
    """Get detailed information about a specific survey"""
    try:
        survey = Survey.query.get_or_404(survey_id)
        
        # Check if user already participated
        existing_response = SurveyResponse.query.filter_by(
            survey_id=survey_id, 
            user_id=current_user.id
        ).first()
        
        if existing_response:
            return jsonify({
                'success': False, 
                'message': 'Sie haben bereits an dieser Umfrage teilgenommen'
            }), 400
        
        if not survey.is_available():
            return jsonify({
                'success': False,
                'message': 'Diese Umfrage ist nicht mehr verfügbar'
            }), 400
        
        survey_data = survey.to_dict()
        survey_data['category_display'] = SURVEY_CATEGORIES.get(survey.category, survey.category)
        
        return jsonify({
            'success': True,
            'survey': survey_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching survey details: {str(e)}")
        return jsonify({'success': False, 'message': 'Fehler beim Laden der Umfrage'}), 500

@surveys_bp.route('/stats', methods=['GET'])
@login_required  
def get_user_survey_stats():
    """Get user's survey statistics"""
    try:
        user_id = current_user.id
        
        # Calculate basic stats
        total_surveys = SurveyResponse.query.filter_by(user_id=user_id).count()
        completed_surveys = SurveyResponse.query.filter_by(
            user_id=user_id,
            status='completed'
        ).count()
        
        total_earnings = db.session.query(db.func.sum(SurveyResponse.earnings_amount))\
            .filter_by(user_id=user_id).scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_surveys_started': total_surveys,
                'total_surveys_completed': completed_surveys,
                'completion_rate': round((completed_surveys / total_surveys * 100) if total_surveys > 0 else 0, 1),
                'total_earnings': float(total_earnings)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching survey stats: {str(e)}")
        return jsonify({'success': False, 'message': 'Fehler beim Laden der Statistiken'}), 500