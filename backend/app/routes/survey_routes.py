from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.database import db
from app.models import Survey, SurveyResponse, SurveyAnswer, SurveyQuestion, Activity, Earning
from datetime import datetime

survey_bp = Blueprint('survey', __name__)

@survey_bp.route('/surveys', methods=['GET'])
@login_required
def get_surveys():
    """Alle verfügbaren Umfragen für den Nutzer abrufen"""
    try:
        # Nur aktive Umfragen, die noch nicht vom Nutzer beantwortet wurden
        completed_survey_ids = db.session.query(SurveyResponse.survey_id).filter(
            SurveyResponse.user_id == current_user.id,
            SurveyResponse.status == 'completed'
        ).subquery()
        
        available_surveys = Survey.query.filter(
            Survey.status == 'active',
            ~Survey.id.in_(completed_survey_ids),
            db.or_(Survey.expires_at == None, Survey.expires_at > datetime.utcnow())
        ).all()
        
        # Umfragen, die der Nutzer begonnen aber nicht abgeschlossen hat
        in_progress = db.session.query(Survey, SurveyResponse).join(
            SurveyResponse, Survey.id == SurveyResponse.survey_id
        ).filter(
            SurveyResponse.user_id == current_user.id,
            SurveyResponse.status == 'started'
        ).all()
        
        return jsonify({
            'available': [survey.to_dict() for survey in available_surveys],
            'inProgress': [{
                **survey.to_dict(),
                'responseId': response.id,
                'startedAt': response.started_at.isoformat()
            } for survey, response in in_progress]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@survey_bp.route('/surveys/<int:survey_id>', methods=['GET'])
@login_required
def get_survey_details(survey_id):
    """Details einer spezifischen Umfrage abrufen"""
    try:
        survey = Survey.query.get_or_404(survey_id)
        
        # Prüfen, ob der Nutzer bereits eine Response hat
        existing_response = SurveyResponse.query.filter_by(
            survey_id=survey_id,
            user_id=current_user.id
        ).first()
        
        survey_data = survey.to_dict()
        survey_data['questions'] = sorted(
            [q.to_dict() for q in survey.questions],
            key=lambda x: x['order']
        )
        
        if existing_response:
            survey_data['responseId'] = existing_response.id
            survey_data['responseStatus'] = existing_response.status
            
            # Bereits gegebene Antworten laden
            if existing_response.status == 'started':
                answers = {}
                for answer in existing_response.answers:
                    if answer.answer_text:
                        answers[answer.question_id] = answer.answer_text
                    elif answer.option_id:
                        answers[answer.question_id] = answer.option_id
                survey_data['existingAnswers'] = answers
        
        return jsonify(survey_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@survey_bp.route('/surveys/<int:survey_id>/start', methods=['POST'])
@login_required
def start_survey(survey_id):
    """Eine neue Umfrage starten"""
    try:
        survey = Survey.query.get_or_404(survey_id)
        
        # Prüfen, ob bereits eine Response existiert
        existing_response = SurveyResponse.query.filter_by(
            survey_id=survey_id,
            user_id=current_user.id
        ).first()
        
        if existing_response:
            if existing_response.status == 'completed':
                return jsonify({'error': 'Survey already completed'}), 400
            else:
                # Fortsetzen einer begonnenen Umfrage
                return jsonify({
                    'responseId': existing_response.id,
                    'message': 'Continuing existing survey'
                })
        
        # Neue Response erstellen
        response = SurveyResponse(
            survey_id=survey_id,
            user_id=current_user.id,
            status='started'
        )
        db.session.add(response)
        db.session.commit()
        
        return jsonify({
            'responseId': response.id,
            'message': 'Survey started successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@survey_bp.route('/surveys/<int:survey_id>/submit', methods=['POST'])
@login_required
def submit_survey(survey_id):
    """Umfrage-Antworten speichern"""
    try:
        survey = Survey.query.get_or_404(survey_id)
        data = request.get_json()
        response_id = data.get('responseId')
        answers = data.get('answers', {})
        
        # Response finden oder erstellen
        if response_id:
            response = SurveyResponse.query.filter_by(
                id=response_id,
                user_id=current_user.id,
                survey_id=survey_id
            ).first()
            if not response:
                return jsonify({'error': 'Invalid response ID'}), 400
        else:
            response = SurveyResponse(
                survey_id=survey_id,
                user_id=current_user.id,
                status='started'
            )
            db.session.add(response)
            db.session.flush()
        
        # Alte Antworten löschen (falls vorhanden)
        SurveyAnswer.query.filter_by(response_id=response.id).delete()
        
        # Neue Antworten speichern
        for question_id, answer_value in answers.items():
            question = SurveyQuestion.query.get(int(question_id))
            if not question or question.survey_id != survey_id:
                continue
            
            answer = SurveyAnswer(response_id=response.id, question_id=question.id)
            
            if question.question_type in ['single', 'multiple']:
                # Multiple Choice Antwort
                if isinstance(answer_value, list):
                    # Multiple Choice mit mehreren Antworten
                    for option_id in answer_value:
                        multi_answer = SurveyAnswer(
                            response_id=response.id,
                            question_id=question.id,
                            option_id=int(option_id)
                        )
                        db.session.add(multi_answer)
                else:
                    answer.option_id = int(answer_value)
                    db.session.add(answer)
            else:
                # Text oder Scale Antwort
                answer.answer_text = str(answer_value)
                db.session.add(answer)
        
        # Response als abgeschlossen markieren
        response.status = 'completed'
        response.completed_at = datetime.utcnow()
        
        # Verdienst hinzufügen
        earning = Earning(
            user_id=current_user.id,
            amount=survey.reward,
            source='survey',
            description=f'Umfrage abgeschlossen: {survey.title}'
        )
        db.session.add(earning)
        
        # Aktivität hinzufügen
        activity = Activity(
            user_id=current_user.id,
            title='Umfrage abgeschlossen',
            description=f'Du hast die Umfrage "{survey.title}" erfolgreich abgeschlossen.',
            activity_type='survey_completed',
            earning=survey.reward,
            company=survey.company
        )
        db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'reward': survey.reward,
            'message': 'Survey completed successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@survey_bp.route('/surveys/<int:survey_id>/save', methods=['POST'])
@login_required
def save_survey_progress(survey_id):
    """Zwischenspeichern von Umfrage-Antworten"""
    try:
        data = request.get_json()
        response_id = data.get('responseId')
        answers = data.get('answers', {})
        
        response = SurveyResponse.query.filter_by(
            id=response_id,
            user_id=current_user.id,
            survey_id=survey_id
        ).first()
        
        if not response:
            return jsonify({'error': 'Invalid response'}), 400
        
        # Alte Antworten für die gegebenen Fragen löschen
        question_ids = [int(qid) for qid in answers.keys()]
        if question_ids:
            SurveyAnswer.query.filter(
                SurveyAnswer.response_id == response.id,
                SurveyAnswer.question_id.in_(question_ids)
            ).delete()
        
        # Neue Antworten speichern
        for question_id, answer_value in answers.items():
            question = SurveyQuestion.query.get(int(question_id))
            if not question or question.survey_id != survey_id:
                continue
            
            if question.question_type in ['single', 'multiple']:
                if isinstance(answer_value, list):
                    for option_id in answer_value:
                        answer = SurveyAnswer(
                            response_id=response.id,
                            question_id=question.id,
                            option_id=int(option_id)
                        )
                        db.session.add(answer)
                else:
                    answer = SurveyAnswer(
                        response_id=response.id,
                        question_id=question.id,
                        option_id=int(answer_value)
                    )
                    db.session.add(answer)
            else:
                answer = SurveyAnswer(
                    response_id=response.id,
                    question_id=question.id,
                    answer_text=str(answer_value)
                )
                db.session.add(answer)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress saved'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@survey_bp.route('/surveys/history', methods=['GET'])
@login_required
def get_survey_history():
    """Historie der abgeschlossenen Umfragen"""
    try:
        completed_surveys = db.session.query(Survey, SurveyResponse).join(
            SurveyResponse, Survey.id == SurveyResponse.survey_id
        ).filter(
            SurveyResponse.user_id == current_user.id,
            SurveyResponse.status == 'completed'
        ).order_by(SurveyResponse.completed_at.desc()).all()
        
        history = []
        for survey, response in completed_surveys:
            history.append({
                'id': survey.id,
                'title': survey.title,
                'company': survey.company,
                'reward': survey.reward,
                'completedAt': response.completed_at.isoformat(),
                'category': survey.category
            })
        
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500