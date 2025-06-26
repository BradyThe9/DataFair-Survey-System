from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_fair.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and initialize database
from app.database import init_db
init_db(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# Import blueprints - NUR die existierenden!
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.data_routes import data_bp
from app.routes.earning_routes import earning_bp
from app.routes.activity_routes import activity_bp
# payment_routes und enterprise_routes erstmal ausgelassen

# Try to import survey system
try:
    from app.routes.surveys import surveys_bp
    SURVEYS_ENABLED = True
    print("✅ Survey system loaded!")
except ImportError as e:
    print(f"⚠️ Survey system disabled: {e}")
    SURVEYS_ENABLED = False

# Register blueprints - nur die existierenden
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(data_bp)
app.register_blueprint(earning_bp)
app.register_blueprint(activity_bp)

# Register survey blueprint if available
if SURVEYS_ENABLED:
    app.register_blueprint(surveys_bp)

# CORS Configuration
try:
    from flask_cors import CORS
    CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
except ImportError:
    print("⚠️ Flask-CORS not available")

# Basic routes for frontend
@app.route('/')
def index():
    return send_from_directory('../frontend/pages', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    # Try pages first, then assets
    if filename.endswith('.html'):
        return send_from_directory('../frontend/pages', filename)
    elif filename.startswith('assets/'):
        return send_from_directory('../frontend', filename)
    else:
        return send_from_directory('../frontend/pages', filename)

def create_demo_user():
    from app.database import db
    from app.models import User
    
    print("Checking for demo user...")
    try:
        demo_user = User.query.filter_by(email='demo@datafair.com').first()
        if not demo_user:
            demo_user = User(
                email='demo@datafair.com',
                first_name='Demo',
                last_name='User',
                password_hash=generate_password_hash('demo123'),
                country='DE',
                newsletter=True
            )
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Demo user created!")
            print("   Email: demo@datafair.com")
            print("   Password: demo123")
        else:
            print("✅ Demo user already exists!")
    except Exception as e:
        print(f"❌ Demo user error: {e}")

def init_sample_surveys():
    if not SURVEYS_ENABLED:
        print("⚠️ Survey system not available")
        return
        
    try:
        from app.database import db
        from app.models import Survey
        
        if Survey.query.count() == 0:
            sample_surveys = [
                {
                    'title': 'Online-Shopping Verhalten 2025',
                    'description': 'Teilen Sie Ihre Online-Shopping-Erfahrungen mit uns.',
                    'company': 'DataFair Research',
                    'category': 'shopping',
                    'base_reward': 2.75,
                    'estimated_duration': 6,
                    'questions': [
                        {
                            'id': 'q1',
                            'type': 'single_choice',
                            'text': 'Was ist Ihnen beim Online-Shopping am wichtigsten?',
                            'options': ['Preis', 'Qualität', 'Schnelle Lieferung', 'Kundenservice'],
                            'required': True
                        }
                    ],
                    'max_responses': 500
                },
                {
                    'title': 'Technologie-Trends 2025',
                    'description': 'Ihre Meinung zu aktuellen Technologie-Trends.',
                    'company': 'TechInsights',
                    'category': 'tech',
                    'base_reward': 4.00,
                    'estimated_duration': 10,
                    'questions': [
                        {
                            'id': 'q1',
                            'type': 'single_choice',
                            'text': 'Welche Technologie wird 2025 am wichtigsten sein?',
                            'options': ['KI', 'VR', 'Blockchain', 'IoT'],
                            'required': True
                        }
                    ],
                    'max_responses': 300
                }
            ]
            
            for survey_data in sample_surveys:
                survey = Survey(
                    title=survey_data['title'],
                    description=survey_data['description'],
                    company=survey_data['company'],
                    category=survey_data['category'],
                    base_reward=survey_data['base_reward'],
                    estimated_duration=survey_data['estimated_duration'],
                    questions=survey_data['questions'],
                    max_responses=survey_data['max_responses'],
                    status='active',
                    expires_at=datetime.utcnow() + timedelta(days=60)
                )
                db.session.add(survey)
            
            db.session.commit()
            print(f"✅ {len(sample_surveys)} sample surveys created!")
        else:
            print(f"✅ {Survey.query.count()} surveys already exist")
            
    except Exception as e:
        print(f"❌ Error creating sample surveys: {e}")
        import traceback
        traceback.print_exc()

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'surveys_enabled': SURVEYS_ENABLED,
        'version': '1.0.0'
    })

if __name__ == '__main__':
    with app.app_context():
        from app.database import db
        
        print("🚀 Initializing DataFair Application...")
        print("=" * 50)
        
        # Create all database tables
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Initialize sample data
        create_demo_user()
        init_sample_surveys()
        
        print("=" * 50)
        print("🎉 DataFair Application Ready!")
        print()
        print("📍 Available at: http://127.0.0.1:5000")
        print("👤 Demo Login: demo@datafair.com / demo123")
        print()
        if SURVEYS_ENABLED:
            print("📋 Survey System: ✅ ACTIVE")
            print("🧪 Test Endpoint: http://127.0.0.1:5000/api/surveys/test")
            print("📋 Available Surveys: http://127.0.0.1:5000/api/surveys/available")
        else:
            print("📋 Survey System: ❌ DISABLED")
        print("=" * 50)
        
    app.run(debug=True, port=5000, host='127.0.0.1')