# backend/app/utils/survey_engine.py
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy import and_, or_
from ..models.survey import Survey, SurveyResponse, QualificationResponse
from .. import db

class SurveyEngine:
    def check_qualification(self, criteria: Dict[str, Any], answers: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Check if user qualifies for survey"""
        try:
            if not criteria:
                return {'qualified': True, 'reason': 'Keine Qualifikationskriterien erforderlich'}
            
            # Check custom qualification questions
            if 'questions' in criteria:
                for question in criteria['questions']:
                    question_id = question['id']
                    required_answer = question.get('required_answer')
                    
                    if question_id not in answers:
                        return {'qualified': False, 'reason': 'Nicht alle Qualifikationsfragen beantwortet'}
                    
                    user_answer = answers[question_id]
                    
                    if required_answer is not None and user_answer != required_answer:
                        return {
                            'qualified': False,
                            'reason': question.get('disqualify_reason', 'Qualifikationskriterien nicht erfüllt')
                        }
                        
            return {'qualified': True, 'reason': 'Alle Qualifikationskriterien erfüllt'}
            
        except Exception as e:
            return {'qualified': False, 'reason': f'Fehler bei der Qualifikationsprüfung: {str(e)}'}
    
    def get_alternative_surveys(self, user_id: int, excluded_category: str = None, limit: int = 5) -> List[Survey]:
        """Get alternative surveys for user"""
        query = db.session.query(Survey).filter(
            and_(
                Survey.status == 'active',
                or_(Survey.expires_at.is_(None), Survey.expires_at > datetime.utcnow()),
                ~Survey.id.in_(
                    db.session.query(SurveyResponse.survey_id).filter(
                        SurveyResponse.user_id == user_id
                    )
                )
            )
        )
        
        if excluded_category:
            query = query.filter(Survey.category != excluded_category)
        
        return query.order_by(Survey.base_reward.desc()).limit(limit).all()