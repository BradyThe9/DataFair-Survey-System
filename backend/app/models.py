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

# ===== UNIFIED SURVEY SYSTEM =====
class Survey(db.Model):
    """Neue einheitliche Umfragen Tabelle"""
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100))
    category = db.Column(db.String(50), nullable=False)  # 'tech', 'lifestyle', 'shopping', etc.
    base_reward = db.Column(db.Float, nullable=False)  # Grundvergütung
    estimated_duration = db.Column(db.Integer, nullable=False)  # Minuten
    
    # JSON Fields für Flexibilität
    qualification_criteria = db.Column(db.JSON)  # Qualifikationskriterien
    questions = db.Column(db.JSON, nullable=False)  # Fragen als JSON Array
    
    # Survey Management
    max_responses = db.Column(db.Integer)  # Maximale Teilnehmer
    current_responses = db.Column(db.Integer, default=0)  # Aktuelle Antworten
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'paused', 'completed'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    responses = db.relationship('SurveyResponse', backref='survey', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'company': self.company,
            'category': self.category,
            'base_reward': self.base_reward,
            'estimated_duration': self.estimated_duration,
            'qualification_criteria': self.qualification_criteria,
            'questions': self.questions,
            'max_responses': self.max_responses,
            'current_responses': self.current_responses,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'question_count': len(self.questions) if self.questions else 0
        }
    
    def is_available(self):
        """Check if survey is available for new participants"""
        if self.status != 'active':
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        if self.max_responses and self.current_responses >= self.max_responses:
            return False
        return True
    
    def get_slots_remaining(self):
        """Get remaining participant slots"""
        if not self.max_responses:
            return None
        return max(0, self.max_responses - self.current_responses)

class SurveyResponse(db.Model):
    """Umfrage-Antworten - vereinfachtes JSON-basiertes System"""
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # JSON für alle Antworten
    answers = db.Column(db.JSON, nullable=False)  # {'q1': 'answer1', 'q2': 'answer2'}
    
    # Status und Progress
    qualification_passed = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Integer, default=0)  # 0-100%
    status = db.Column(db.String(20), default='started')  # 'started', 'completed', 'abandoned'
    
    # Earnings
    earnings_amount = db.Column(db.Float, default=0.00)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Constraint: Ein User kann nur einmal pro Umfrage teilnehmen
    __table_args__ = (db.UniqueConstraint('survey_id', 'user_id', name='unique_user_survey'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'user_id': self.user_id,
            'answers': self.answers,
            'qualification_passed': self.qualification_passed,
            'completion_percentage': self.completion_percentage,
            'status': self.status,
            'earnings_amount': self.earnings_amount,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def is_completed(self):
        """Check if survey response is completed"""
        return self.status == 'completed' and self.completed_at is not None
    
    def calculate_earnings(self):
        """Calculate earnings based on completion"""
        if not self.qualification_passed:
            return 0.00
        
        if self.completion_percentage >= 100:
            return float(self.survey.base_reward)
        elif self.completion_percentage >= 50:  # Partial completion minimum
            return float(self.survey.base_reward) * (self.completion_percentage / 100.0)
        else:
            return 0.00

# ===== LEGACY SURVEY SYSTEM (für Kompatibilität - falls alte Daten existieren) =====
class SurveyQuestion(db.Model):
    """Legacy Survey Questions - für Abwärtskompatibilität"""
    __tablename__ = 'survey_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)
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
    """Legacy Survey Question Options"""
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

class SurveyAnswer(db.Model):
    """Legacy Survey Answers"""
    __tablename__ = 'survey_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_questions.id'), nullable=False)
    answer_text = db.Column(db.Text)
    option_id = db.Column(db.Integer, db.ForeignKey('survey_question_options.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'questionId': self.question_id,
            'answerText': self.answer_text,
            'optionId': self.option_id,
            'createdAt': self.created_at.isoformat()
        }

# ===== SURVEY SYSTEM CONSTANTS =====
SURVEY_CATEGORIES = {
    'tech': 'Technologie',
    'lifestyle': 'Lifestyle',
    'shopping': 'Shopping',
    'health': 'Gesundheit',
    'travel': 'Reisen',
    'finance': 'Finanzen',
    'education': 'Bildung',
    'entertainment': 'Unterhaltung'
}

SURVEY_STATUS = {
    'active': 'Aktiv',
    'paused': 'Pausiert',
    'completed': 'Abgeschlossen',
    'archived': 'Archiviert'
}

QUESTION_TYPES = {
    'single_choice': 'Einzelauswahl',
    'multiple_choice': 'Mehrfachauswahl',
    'scale': 'Bewertungsskala',
    'text': 'Textantwort',
    'number': 'Zahleneingabe',
    'email': 'E-Mail',
    'date': 'Datum',
    'boolean': 'Ja/Nein'
}