# backend/app/models/survey_models.py
from datetime import datetime
from app.database import db

class Survey(db.Model):
    """Umfragen Tabelle"""
    __tablename__ = 'surveys'
    __table_args__ = {'extend_existing': True}  # Fix für Table-Konflikt
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    base_reward = db.Column(db.Float, nullable=False)
    estimated_duration = db.Column(db.Integer, nullable=False)
    qualification_criteria = db.Column(db.JSON)
    questions = db.Column(db.JSON, nullable=False)
    max_responses = db.Column(db.Integer)
    current_responses = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'base_reward': self.base_reward,
            'estimated_duration': self.estimated_duration,
            'qualification_criteria': self.qualification_criteria,
            'questions': self.questions,
            'max_responses': self.max_responses,
            'current_responses': self.current_responses,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def is_available(self):
        if self.status != 'active':
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        if self.max_responses and self.current_responses >= self.max_responses:
            return False
        return True


class SurveyResponse(db.Model):
    """Umfrage-Antworten"""
    __tablename__ = 'survey_responses'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    qualification_passed = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Integer, default=0)
    earnings_amount = db.Column(db.Float, default=0.00)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    survey = db.relationship('Survey', backref='responses')
    
    __table_args__ = (
        db.UniqueConstraint('survey_id', 'user_id', name='unique_user_survey'),
        {'extend_existing': True}
    )


# Survey Categories
SURVEY_CATEGORIES = {
    'tech': 'Technologie',
    'lifestyle': 'Lifestyle',
    'shopping': 'Shopping',
    'health': 'Gesundheit',
    'travel': 'Reisen',
    'finance': 'Finanzen'
}