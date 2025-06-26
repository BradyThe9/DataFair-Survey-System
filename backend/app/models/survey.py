# backend/app/models/survey.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

# Import your existing db instance
from .. import db  # Assuming you have db in your main app

class Survey(db.Model):
    """Umfragen Tabelle - Speichert alle verfügbaren Umfragen"""
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    base_reward = db.Column(db.DECIMAL(10, 2), nullable=False)
    estimated_duration = db.Column(db.Integer, nullable=False)
    qualification_criteria = db.Column(db.JSON)
    questions = db.Column(db.JSON, nullable=False)
    max_responses = db.Column(db.Integer)
    current_responses = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    responses = relationship("SurveyResponse", back_populates="survey")
    qualifications = relationship("QualificationResponse", back_populates="survey")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'base_reward': float(self.base_reward),
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
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    qualification_passed = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Integer, default=0)
    earnings_amount = db.Column(db.DECIMAL(10, 2), default=0.00)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    survey = relationship("Survey", back_populates="responses")
    
    __table_args__ = (db.UniqueConstraint('survey_id', 'user_id', name='unique_user_survey'),)
    
    def is_completed(self):
        return self.completion_percentage >= 100 and self.completed_at is not None
    
    def calculate_earnings(self):
        if not self.qualification_passed:
            return 0.00
        if self.completion_percentage >= 100:
            return float(self.survey.base_reward)
        elif self.completion_percentage >= 50:
            return float(self.survey.base_reward) * (self.completion_percentage / 100.0)
        else:
            return 0.00


class QualificationResponse(db.Model):
    """Qualifikations-Antworten"""
    __tablename__ = 'qualification_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    qualified = db.Column(db.Boolean, nullable=False)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    survey = relationship("Survey", back_populates="qualifications")


# Constants
SURVEY_CATEGORIES = {
    'tech': 'Technologie',
    'lifestyle': 'Lifestyle',
    'shopping': 'Shopping',
    'health': 'Gesundheit',
    'travel': 'Reisen',
    'finance': 'Finanzen'
}