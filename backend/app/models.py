from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date)
    country = db.Column(db.String(2), default='DE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    newsletter = db.Column(db.Boolean, default=False)
    
    # Relationships
    data_permissions = db.relationship('DataPermission', backref='user', lazy=True)
    earnings = db.relationship('Earning', backref='user', lazy=True)
    payouts = db.relationship('Payout', backref='user', lazy=True)
    activities = db.relationship('Activity', backref='user', lazy=True)
    survey_responses = db.relationship('SurveyResponse', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'birthDate': self.birth_date.isoformat() if self.birth_date else None,
            'country': self.country,
            'joinDate': self.created_at.isoformat(),
            'newsletter': self.newsletter
        }

class DataType(db.Model):
    __tablename__ = 'data_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(10))
    monthly_value = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50))
    
    # Relationships
    permissions = db.relationship('DataPermission', backref='data_type', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'monthlyValue': self.monthly_value,
            'category': self.category
        }

class DataPermission(db.Model):
    __tablename__ = 'data_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_type_id = db.Column(db.Integer, db.ForeignKey('data_types.id'), nullable=False)
    enabled = db.Column(db.Boolean, default=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'dataTypeId': self.data_type_id,
            'enabled': self.enabled,
            'grantedAt': self.granted_at.isoformat(),
            'lastAccessed': self.last_accessed.isoformat() if self.last_accessed else None
        }

class Earning(db.Model):
    __tablename__ = 'earnings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50))  # 'data_share', 'survey', 'bonus'
    description = db.Column(db.Text)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'source': self.source,
            'description': self.description,
            'earnedAt': self.earned_at.isoformat()
        }

class Payout(db.Model):
    __tablename__ = 'payouts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20))  # 'paypal', 'bank', 'crypto'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'processing', 'completed'
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'method': self.method,
            'status': self.status,
            'date': self.requested_at.strftime('%d.%m.%Y'),
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    activity_type = db.Column(db.String(50))  # 'data_usage', 'survey_completed', 'bonus'
    earning = db.Column(db.Float, default=0.0)
    company = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        # Zeit-Differenz berechnen für die Anzeige
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            if diff.days == 1:
                timestamp = "Gestern"
            else:
                timestamp = f"Vor {diff.days} Tagen"
        else:
            hours = diff.seconds // 3600
            if hours > 0:
                timestamp = f"Vor {hours} Stunden" if hours > 1 else "Vor 1 Stunde"
            else:
                minutes = diff.seconds // 60
                if minutes > 0:
                    timestamp = f"Vor {minutes} Minuten" if minutes > 1 else "Vor 1 Minute"
                else:
                    timestamp = "Gerade eben"
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'timestamp': timestamp,
            'earning': self.earning,
            'company': self.company,
            'type': self.activity_type
        }

# Survey Models
class Survey(db.Model):
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    company = db.Column(db.String(100))
    reward = db.Column(db.Float, nullable=False)
    estimated_time = db.Column(db.Integer)  # in minutes
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # 'active', 'paused', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    questions = db.relationship('SurveyQuestion', backref='survey', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('SurveyResponse', backref='survey', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'company': self.company,
            'reward': self.reward,
            'estimatedTime': self.estimated_time,
            'category': self.category,
            'status': self.status,
            'createdAt': self.created_at.isoformat(),
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
            'questionCount': len(self.questions)
        }

class SurveyQuestion(db.Model):
    __tablename__ = 'survey_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # 'single', 'multiple', 'text', 'scale'
    order = db.Column(db.Integer, default=0)
    required = db.Column(db.Boolean, default=True)
    
    # Relationships
    options = db.relationship('SurveyQuestionOption', backref='question', lazy=True, cascade='all, delete-orphan')
    answers = db.relationship('SurveyAnswer', backref='question', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.question_text,
            'type': self.question_type,
            'order': self.order,
            'required': self.required,
            'options': [opt.to_dict() for opt in self.options]
        }

class SurveyQuestionOption(db.Model):
    __tablename__ = 'survey_question_options'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_questions.id'), nullable=False)
    option_text = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.option_text,
            'order': self.order
        }

class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='started')  # 'started', 'completed', 'abandoned'
    
    # Relationships
    answers = db.relationship('SurveyAnswer', backref='response', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'surveyId': self.survey_id,
            'startedAt': self.started_at.isoformat(),
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status
        }

class SurveyAnswer(db.Model):
    __tablename__ = 'survey_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_questions.id'), nullable=False)
    answer_text = db.Column(db.Text)  # Für Textantworten
    option_id = db.Column(db.Integer, db.ForeignKey('survey_question_options.id'))  # Für Multiple Choice
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'questionId': self.question_id,
            'answerText': self.answer_text,
            'optionId': self.option_id,
            'createdAt': self.created_at.isoformat()
        }