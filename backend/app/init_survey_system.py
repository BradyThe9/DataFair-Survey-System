# backend/app/init_survey_system.py
"""
Survey System Initialization Script
Führe dieses Script aus, um das Umfragen-System zu initialisieren
"""

from datetime import datetime, timedelta
from flask import current_app
from .models.survey import Survey, db, SURVEY_CATEGORIES
from .utils.survey_engine import SurveyEngine


def create_sample_surveys():
    """Erstelle Beispiel-Umfragen für das System"""
    
    surveys_data = [
        {
            'title': 'Technologie-Trends 2025',
            'description': 'Teilen Sie Ihre Meinung zu aktuellen Technologie-Trends und helfen Sie uns die Zukunft zu verstehen.',
            'category': 'tech',
            'base_reward': 4.00,
            'estimated_duration': 10,
            'max_responses': 300,
            'qualification_criteria': {
                'demographics': {
                    'age': {'min': 18, 'max': 65},
                    'location': ['Germany', 'Austria', 'Switzerland']
                },
                'questions': [
                    {
                        'id': 'tech_interest',
                        'text': 'Interessieren Sie sich für neue Technologien?',
                        'type': 'boolean',
                        'required_answer': True,
                        'disqualify_reason': 'Diese Umfrage richtet sich an Technologie-Interessierte'
                    }
                ]
            },
            'questions': [
                {
                    'id': 'q1',
                    'type': 'single_choice',
                    'text': 'Welche Technologie wird Ihrer Meinung nach 2025 am wichtigsten sein?',
                    'options': ['Künstliche Intelligenz', 'Virtual Reality', 'Blockchain', 'IoT', 'Quantum Computing'],
                    'required': True
                },
                {
                    'id': 'q2',
                    'type': 'scale',
                    'text': 'Wie besorgt sind Sie über den Datenschutz bei neuen Technologien?',
                    'scale_min': 1,
                    'scale_max': 5,
                    'scale_labels': ['Gar nicht besorgt', 'Wenig besorgt', 'Neutral', 'Besorgt', 'Sehr besorgt'],
                    'required': True
                },
                {
                    'id': 'q3',
                    'type': 'multiple_choice',
                    'text': 'Welche Tech-Geräte nutzen Sie täglich? (Mehrfachauswahl)',
                    'options': ['Smartphone', 'Laptop', 'Tablet', 'Smart Watch', 'Smart Speaker', 'VR-Brille'],
                    'required': True
                }
            ]
        },
        {
            'title': 'Lifestyle & Gesundheit Studie',
            'description': 'Helfen Sie uns zu verstehen, wie sich Lifestyle-Trends auf die Gesundheit auswirken.',
            'category': 'lifestyle',
            'base_reward': 3.50,
            'estimated_duration': 8,
            'max_responses': 400,
            'qualification_criteria': {
                'demographics': {
                    'age': {'min': 18, 'max': 75}
                }
            },
            'questions': [
                {
                    'id': 'q1',
                    'type': 'single_choice',
                    'text': 'Wie oft treiben Sie Sport pro Woche?',
                    'options': ['Nie', '1-2 mal', '3-4 mal', '5+ mal', 'Täglich'],
                    'required': True
                },
                {
                    'id': 'q2',
                    'type': 'scale',
                    'text': 'Wie würden Sie Ihr allgemeines Wohlbefinden bewerten?',
                    'scale_min': 1,
                    'scale_max': 10,
                    'scale_labels': ['Sehr schlecht', 'Ausgezeichnet'],
                    'required': True
                },
                {
                    'id': 'q3',
                    'type': 'text',
                    'text': 'Was motiviert Sie am meisten, gesund zu leben?',
                    'required': False
                }
            ]
        },
        {
            'title': 'Online-Shopping Verhalten 2025',
            'description': 'Teilen Sie Ihre Online-Shopping-Erfahrungen und helfen Sie E-Commerce zu verbessern.',
            'category': 'shopping',
            'base_reward': 2.75,
            'estimated_duration': 6,
            'max_responses': 600,
            'qualification_criteria': {
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
            'questions': [
                {
                    'id': 'q1',
                    'type': 'single_choice',
                    'text': 'Was ist Ihnen beim Online-Shopping am wichtigsten?',
                    'options': ['Preis', 'Qualität', 'Schnelle Lieferung', 'Einfache Rückgabe', 'Kundenservice'],
                    'required': True
                },
                {
                    'id': 'q2',
                    'type': 'multiple_choice',
                    'text': 'Auf welchen Geräten kaufen Sie online ein?',
                    'options': ['Desktop Computer', 'Laptop', 'Smartphone', 'Tablet'],
                    'required': True
                },
                {
                    'id': 'q3',
                    'type': 'scale',
                    'text': 'Wie zufrieden sind Sie mit Ihrem Online-Shopping-Erlebnis?',
                    'scale_min': 1,
                    'scale_max': 5,
                    'required': True
                }
            ]
        },
        {
            'title': 'Finanzplanung & Investment Trends',
            'description': 'Verstehen Sie aktuelle Investment-Trends und teilen Sie Ihre Finanzstrategie.',
            'category': 'finance',
            'base_reward': 5.00,
            'estimated_duration': 15,
            'max_responses': 200,
            'qualification_criteria': {
                'demographics': {
                    'age': {'min': 25, 'max': 65},
                    'income': {'min': 30000}
                },
                'questions': [
                    {
                        'id': 'has_investments',
                        'text': 'Haben Sie bereits Geld investiert oder planen Sie es?',
                        'type': 'boolean',
                        'required_answer': True,
                        'disqualify_reason': 'Diese Umfrage richtet sich an Personen mit Investment-Interesse'
                    }
                ]
            },
            'questions': [
                {
                    'id': 'q1',
                    'type': 'multiple_choice',
                    'text': 'In welche Anlageklassen haben Sie bereits investiert?',
                    'options': ['Aktien', 'ETFs', 'Kryptowährungen', 'Immobilien', 'Anleihen', 'Rohstoffe'],
                    'required': True
                },
                {
                    'id': 'q2',
                    'type': 'scale',
                    'text': 'Wie risikobereit sind Sie bei Investments?',
                    'scale_min': 1,
                    'scale_max': 5,
                    'scale_labels': ['Sehr risikoscheu', 'Risikoscheu', 'Ausgewogen', 'Risikofreudig', 'Sehr risikofreudig'],
                    'required': True
                },
                {
                    'id': 'q3',
                    'type': 'single_choice',
                    'text': 'Welcher Investment-Horizont passt zu Ihnen?',
                    'options': ['Kurzfristig (< 1 Jahr)', 'Mittelfristig (1-5 Jahre)', 'Langfristig (5-10 Jahre)', 'Sehr langfristig (10+ Jahre)'],
                    'required': True
                }
            ]
        },
        {
            'title': 'Reise & Urlaub Präferenzen',
            'description': 'Teilen Sie Ihre Reisegewohnheiten und helfen Sie die Tourismusbranche zu verstehen.',
            'category': 'travel',
            'base_reward': 3.25,
            'estimated_duration': 7,
            'max_responses': 350,
            'qualification_criteria': {
                'questions': [
                    {
                        'id': 'travels_yearly',
                        'text': 'Verreisen Sie mindestens einmal pro Jahr?',
                        'type': 'boolean',
                        'required_answer': True,
                        'disqualify_reason': 'Diese Umfrage richtet sich an Menschen, die regelmäßig verreisen'
                    }
                ]
            },
            'questions': [
                {
                    'id': 'q1',
                    'type': 'single_choice',
                    'text': 'Welche Art von Urlaub bevorzugen Sie?',
                    'options': ['Strandurlaub', 'Städtetrip', 'Naturerlebnis', 'Kulturreise', 'Abenteuerurlaub'],
                    'required': True
                },
                {
                    'id': 'q2',
                    'type': 'scale',
                    'text': 'Wie wichtig ist Ihnen Nachhaltigkeit beim Reisen?',
                    'scale_min': 1,
                    'scale_max': 5,
                    'scale_labels': ['Unwichtig', 'Wenig wichtig', 'Neutral', 'Wichtig', 'Sehr wichtig'],
                    'required': True
                },
                {
                    'id': 'q3',
                    'type': 'multiple_choice',
                    'text': 'Wie buchen Sie normalerweise Ihre Reisen?',
                    'options': ['Online-Reiseportale', 'Direkt beim Anbieter', 'Reisebüro', 'Social Media', 'Empfehlungen'],
                    'required': True
                }
            ]
        }
    ]
    
    created_surveys = []
    
    for survey_data in surveys_data:
        # Check if survey already exists
        existing = Survey.query.filter_by(title=survey_data['title']).first()
        if existing:
            print(f"Survey '{survey_data['title']}' already exists, skipping...")
            continue
        
        survey = Survey(
            title=survey_data['title'],
            description=survey_data['description'],
            category=survey_data['category'],
            base_reward=survey_data['base_reward'],
            estimated_duration=survey_data['estimated_duration'],
            qualification_criteria=survey_data['qualification_criteria'],
            questions=survey_data['questions'],
            max_responses=survey_data['max_responses'],
            status='active',
            expires_at=datetime.utcnow() + timedelta(days=60)  # 60 days from now
        )
        
        db.session.add(survey)
        created_surveys.append(survey)
        print(f"Created survey: {survey_data['title']}")
    
    try:
        db.session.commit()
        print(f"Successfully created {len(created_surveys)} surveys!")
        return created_surveys
    except Exception as e:
        db.session.rollback()
        print(f"Error creating surveys: {str(e)}")
        return []


def init_survey_system():
    """Initialize the complete survey system"""
    
    print("🚀 Initializing DataFair Survey System...")
    
    # Create database tables (if using direct SQLAlchemy)
    try:
        db.create_all()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        return False
    
    # Create sample surveys
    try:
        surveys = create_sample_surveys()
        print(f"✅ Created {len(surveys)} sample surveys")
    except Exception as e:
        print(f"❌ Error creating sample surveys: {str(e)}")
        return False
    
    # Initialize survey engine
    try:
        engine = SurveyEngine()
        print("✅ Survey engine initialized")
    except Exception as e:
        print(f"❌ Error initializing survey engine: {str(e)}")
        return False
    
    print("\n🎉 Survey System successfully initialized!")
    print("\nNext steps:")
    print("1. Add survey routes to your Flask app:")
    print("   from app.routes.surveys import surveys_bp")
    print("   app.register_blueprint(surveys_bp)")
    print("\n2. Test the API endpoints:")
    print("   GET /api/surveys/available")
    print("   GET /api/surveys/{id}")
    print("   POST /api/surveys/{id}/qualify")
    print("\n3. Integrate with your frontend dashboard")
    
    return True


def get_survey_system_status():
    """Get current status of the survey system"""
    
    status = {
        'surveys_total': Survey.query.count(),
        'surveys_active': Survey.query.filter_by(status='active').count(),
        'surveys_by_category': {},
        'total_responses': db.session.query(SurveyResponse).count(),
        'total_earnings_paid': 0
    }
    
    # Count by category
    for category_key, category_name in SURVEY_CATEGORIES.items():
        count = Survey.query.filter_by(category=category_key).count()
        if count > 0:
            status['surveys_by_category'][category_name] = count
    
    # Calculate total earnings
    try:
        from sqlalchemy import func
        total_earnings = db.session.query(func.sum(SurveyResponse.earnings_amount)).scalar()
        status['total_earnings_paid'] = float(total_earnings or 0)
    except:
        status['total_earnings_paid'] = 0
    
    return status


if __name__ == "__main__":
    # If running as script
    print("This script should be imported and run within Flask app context")
    print("Example usage:")
    print("from app.init_survey_system import init_survey_system")
    print("init_survey_system()")