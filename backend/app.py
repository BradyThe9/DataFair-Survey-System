# Hier ist ein Beispiel, wie deine app.py aussehen sollte:

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_fair.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Import your existing models here
# ... your existing User and other models ...

# Import and register survey blueprint
from app.routes.surveys import surveys_bp
app.register_blueprint(surveys_bp)

# Your existing routes and functions...

# Add survey initialization
def init_survey_tables():
    """Initialize survey tables and sample data"""
    try:
        from app.models.survey import Survey
        
        if Survey.query.count() == 0:
            sample_survey = Survey(
                title='Online-Shopping Verhalten 2025',
                description='Teilen Sie Ihre Online-Shopping-Erfahrungen mit uns.',
                category='shopping',
                base_reward=2.75,
                estimated_duration=6,
                qualification_criteria={
                    'questions': [
                        {
                            'id': 'shops_online',
                            'text': 'Kaufen Sie mindestens einmal pro Monat online ein?',
                            'type': 'boolean',
                            'required_answer': True,
                            'disqualify_reason': 'Diese Umfrage richtet sich an regelmäßige Online-Shopper'
                        }
                    ]
                },
                questions=[
                    {
                        'id': 'q1',
                        'type': 'single_choice',
                        'text': 'Was ist Ihnen beim Online-Shopping am wichtigsten?',
                        'options': ['Preis', 'Qualität', 'Schnelle Lieferung', 'Kundenservice'],
                        'required': True
                    }
                ],
                max_responses=500,
                status='active'
            )
            
            db.session.add(sample_survey)
            db.session.commit()
            print("✅ Sample survey created!")
        
    except Exception as e:
        print(f"❌ Error initializing surveys: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Your existing initialization...
        init_survey_tables()  # Add this line
        
    app.run(debug=True, port=5000)