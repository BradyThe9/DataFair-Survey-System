#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Models for DataFair Survey System
"""

from datetime import datetime
from flask_login import UserMixin
from .database import db

class User(UserMixin, db.Model):
    """User Model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Account status
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    survey_responses = db.relationship('SurveyResponse', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Survey(db.Model):
    """Survey Model"""
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Survey content (stored as JSON)
    questions = db.Column(db.Text)  # JSON string of questions
    
    # Survey settings
    reward_amount = db.Column(db.Numeric(10, 2), default=0.00)
    estimated_duration = db.Column(db.Integer, default=5)  # minutes
    max_responses = db.Column(db.Integer, default=1000)
    total_responses = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    starts_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    
    # Relationships
    responses = db.relationship('SurveyResponse', backref='survey', lazy='dynamic')
    
    def __repr__(self):
        return f'<Survey {self.title}>'
    
    @property
    def response_rate(self):
        """Calculate response rate percentage"""
        if self.max_responses == 0:
            return 0
        return (self.total_responses / self.max_responses) * 100
    
    @property
    def is_full(self):
        """Check if survey has reached maximum responses"""
        return self.total_responses >= self.max_responses
    
    def to_dict(self, include_questions=False):
        """Convert survey to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'reward_amount': float(self.reward_amount),
            'estimated_duration': self.estimated_duration,
            'max_responses': self.max_responses,
            'total_responses': self.total_responses,
            'response_rate': self.response_rate,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'is_full': self.is_full,
            'created_at': self.created_at.isoformat(),
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'ends_at': self.ends_at.isoformat() if self.ends_at else None
        }
        
        if include_questions and self.questions:
            import json
            try:
                data['questions'] = json.loads(self.questions) if isinstance(self.questions, str) else self.questions
            except:
                data['questions'] = []
        
        return data

class SurveyResponse(db.Model):
    """Survey Response Model"""
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    
    # Response data (stored as JSON)
    responses = db.Column(db.Text)  # JSON string of user responses
    
    # Metadata
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_completed = db.Column(db.Boolean, default=False)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'survey_id', name='unique_user_survey'),
    )
    
    def __repr__(self):
        return f'<SurveyResponse User:{self.user_id} Survey:{self.survey_id}>'
    
    @property
    def completion_time(self):
        """Calculate time taken to complete survey"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None
    
    def to_dict(self, include_responses=False):
        """Convert survey response to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'survey_id': self.survey_id,
            'is_completed': self.is_completed,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'completion_time': str(self.completion_time) if self.completion_time else None
        }
        
        if include_responses and self.responses:
            import json
            try:
                data['responses'] = json.loads(self.responses) if isinstance(self.responses, str) else self.responses
            except:
                data['responses'] = {}
        
        return data

class DataType(db.Model):
    """Data Type Model - Verfügbare Datentypen für Nutzer"""
    __tablename__ = 'data_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(10))  # Emoji icons
    monthly_value = db.Column(db.Numeric(10, 2), default=0.00)  # Monatlicher Wert in EUR
    category = db.Column(db.String(50))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('DataPermission', backref='data_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<DataType {self.name}>'
    
    def to_dict(self):
        """Convert data type to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'monthly_value': float(self.monthly_value),
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class DataPermission(db.Model):
    """Data Permission Model for user consent management"""
    __tablename__ = 'data_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys - KORRIGIERT!
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_type_id = db.Column(db.Integer, db.ForeignKey('data_types.id'), nullable=False)  # <- GEÄNDERT VON STRING ZU FK
    
    # Permission status
    enabled = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    granted_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='data_permissions')
    # data_type relationship wird von DataType.permissions backref erstellt
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'data_type_id', name='unique_user_data_type'),
    )
    
    def __repr__(self):
        return f'<DataPermission User:{self.user_id} DataType:{self.data_type_id}>'
    
    def to_dict(self):
        """Convert data permission to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'data_type_id': self.data_type_id,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }

class Earning(db.Model):
    """Earning Model to track user earnings"""
    __tablename__ = 'earnings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    survey_response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'))
    
    # Earning details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)  # 'survey', 'data_sharing', 'bonus'
    description = db.Column(db.String(200))
    
    # Status
    status = db.Column(db.String(20), default='earned')  # 'earned', 'paid', 'pending'
    
    # Timestamps
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='earnings')
    survey_response = db.relationship('SurveyResponse', backref='earning')
    
    def __repr__(self):
        return f'<Earning User:{self.user_id} Amount:{self.amount}>'
    
    def to_dict(self):
        """Convert earning to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'source_type': self.source_type,
            'description': self.description,
            'status': self.status,
            'earned_at': self.earned_at.isoformat(),
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }

class Payout(db.Model):
    """Payout Model to track user payout requests"""
    __tablename__ = 'payouts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Payout details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(50), nullable=False)  # 'paypal', 'bank', 'crypto'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'processing', 'completed', 'failed'
    
    # External reference (e.g., PayPal transaction ID)
    external_id = db.Column(db.String(100))
    
    # Timestamps
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='payouts')
    
    def __repr__(self):
        return f'<Payout User:{self.user_id} Amount:{self.amount} Status:{self.status}>'
    
    def to_dict(self):
        """Convert payout to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'method': self.method,
            'status': self.status,
            'external_id': self.external_id,
            'requested_at': self.requested_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }