#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataFair Survey System - Main Application
Flask Backend mit korrigierter Flask-Login Konfiguration + Dashboard
"""

import os
import sys
from datetime import datetime
from flask import Flask, render_template, send_from_directory, jsonify, redirect, url_for, request
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import our modules
from app.database import db, init_db
from app.models import User, Survey, SurveyResponse
from config import Config

def create_app():
    """Application Factory Pattern"""
    app = Flask(__name__, 
                static_folder='../frontend',
                template_folder='../frontend/pages')
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize database
    init_db(app)
    
    # CORS Configuration - Korrigiert für alle Origins
    CORS(app, 
         origins=["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:3000"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Flask-Login Configuration - KORRIGIERT
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Korrigierter Endpoint
    login_manager.login_message = 'Bitte melde dich an, um auf diese Seite zuzugreifen.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.surveys import surveys_bp
    from app.routes.dashboard_routes import dashboard_bp  # NEU!
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(surveys_bp, url_prefix='/api/surveys')
    app.register_blueprint(dashboard_bp)  # NEU! Dashboard hat bereits /api/dashboard prefix
    
    # Frontend Routes - Korrigierte Reihenfolge
    @app.route('/')
    def index():
        """Startseite"""
        return send_from_directory('../frontend/pages', 'index.html')
    
    @app.route('/index.html')
    def index_alt():
        """Alternative Startseite Route"""
        return send_from_directory('../frontend/pages', 'index.html')
    
    @app.route('/pages/index.html')
    def index_pages():
        """Startseite über /pages/ Route"""
        return send_from_directory('../frontend/pages', 'index.html')
    
    @app.route('/login.html')
    def login_page():
        """Login-Seite"""
        return send_from_directory('../frontend/pages', 'login.html')
    
    @app.route('/pages/login.html')
    def login_page_pages():
        """Login-Seite über /pages/ Route"""
        return send_from_directory('../frontend/pages', 'login.html')
    
    @app.route('/register.html')
    def register_page():
        """Registrierung-Seite"""
        return send_from_directory('../frontend/pages', 'register.html')
    
    @app.route('/pages/register.html')
    def register_page_pages():
        """Registrierung-Seite über /pages/ Route"""
        return send_from_directory('../frontend/pages', 'register.html')
    
    @app.route('/dashboard.html')
    @login_required
    def dashboard_page():
        """Dashboard-Seite (Login erforderlich)"""
        return send_from_directory('../frontend/pages', 'dashboard.html')
    
    @app.route('/pages/dashboard.html')
    @login_required
    def dashboard_page_pages():
        """Dashboard-Seite über /pages/ Route (Login erforderlich)"""
        return send_from_directory('../frontend/pages', 'dashboard.html')
    
    @app.route('/enterprise.html')
    def enterprise_page():
        """Enterprise-Seite"""
        return send_from_directory('../frontend/pages', 'enterprise.html')
    
    @app.route('/pages/enterprise.html')
    def enterprise_page_pages():
        """Enterprise-Seite über /pages/ Route"""
        return send_from_directory('../frontend/pages', 'enterprise.html')
    
    # Static Files and Assets - Erweitert
    @app.route('/assets/<path:filename>')
    def assets(filename):
        """Serve static assets"""
        return send_from_directory('../frontend/assets', filename)
    
    @app.route('/frontend/assets/<path:filename>')
    def frontend_assets(filename):
        """Alternative asset route"""
        return send_from_directory('../frontend/assets', filename)
        
    @app.route('/pages/<path:filename>')
    def pages_fallback(filename):
        """Fallback for any /pages/ requests"""
        try:
            return send_from_directory('../frontend/pages', filename)
        except:
            return "Page not found", 404
    
    # Favicon
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory('../frontend/assets/images', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    # Health Check
    @app.route('/health')
    def health_check():
        """System Health Check"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'surveys_enabled': True,
            'dashboard_enabled': True  # NEU!
        })
    
    # API Documentation
    @app.route('/api')
    def api_docs():
        """API Documentation"""
        return jsonify({
            'message': 'DataFair Survey System API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/auth/',
                'surveys': '/api/surveys/',
                'dashboard': '/api/dashboard/',  # NEU!
                'users': '/api/users/',
                'health': '/health'
            }
        })
    
    # Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

def create_demo_data():
    """Create demo user and sample surveys"""
    print("Checking for demo user...")
    
    # Check if demo user exists
    demo_user = User.query.filter_by(email='demo@datafair.com').first()
    
    if not demo_user:
        # Create demo user
        demo_user = User(
            email='demo@datafair.com',
            password_hash=generate_password_hash('demo123'),
            first_name='Demo',
            last_name='User',
            is_verified=True
        )
        db.session.add(demo_user)
        print("✅ Demo user created!")
        print("Email: demo@datafair.com")
        print("Password: demo123")
    else:
        print("✅ Demo user already exists!")
    
    # Check for surveys
    survey_count = Survey.query.count()
    
    if survey_count == 0:
        # Create sample surveys
        import json
        
        survey1_questions = [
            {
                "id": 1,
                "question": "Wie oft kaufen Sie online ein?",
                "type": "multiple_choice",
                "options": ["Täglich", "Wöchentlich", "Monatlich", "Selten"]
            },
            {
                "id": 2,
                "question": "Was ist Ihnen beim Online-Shopping am wichtigsten?",
                "type": "multiple_choice",
                "options": ["Preis", "Qualität", "Lieferzeit", "Nachhaltigkeit"]
            }
        ]
        
        survey2_questions = [
            {
                "id": 1,
                "question": "Wie viele Stunden pro Tag nutzen Sie Ihr Smartphone?",
                "type": "multiple_choice",
                "options": ["1-2 Stunden", "3-4 Stunden", "5-6 Stunden", "Mehr als 6 Stunden"]
            },
            {
                "id": 2,
                "question": "Welche Apps nutzen Sie am häufigsten?",
                "type": "multiple_choice",
                "options": ["Social Media", "Nachrichten", "Shopping", "Games"]
            }
        ]
        
        survey1 = Survey(
            title="Konsumverhalten Studie 2025",
            description="Eine Umfrage über moderne Konsumgewohnheiten",
            questions=json.dumps(survey1_questions),  # Convert to JSON string
            reward_amount=15.50,
            max_responses=1000,
            is_active=True
        )
        
        survey2 = Survey(
            title="Technologie-Nutzung im Alltag",
            description="Umfrage zur Nutzung digitaler Technologien",
            questions=json.dumps(survey2_questions),  # Convert to JSON string
            reward_amount=12.00,
            max_responses=500,
            is_active=True
        )
        
        db.session.add(survey1)
        db.session.add(survey2)
        print("✅ 2 sample surveys created!")
    else:
        print(f"✅ {survey_count} surveys already exist")
    
    db.session.commit()

if __name__ == '__main__':
    print("✅ Survey system loaded!")
    print("✅ Dashboard system loaded!")  # NEU!
    print("🚀 Initializing DataFair Application...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    # Create tables and demo data
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
        create_demo_data()
    
    print("=" * 50)
    print("🎉 DataFair Application Ready!")
    print(f"📍 Available at: http://127.0.0.1:5000")
    print(f"👤 Demo Login: demo@datafair.com / demo123")
    print(f"📋 Survey System: ✅ ACTIVE")
    print(f"📊 Dashboard System: ✅ ACTIVE")  # NEU!
    print(f"🧪 Test Endpoint: http://127.0.0.1:5000/api/surveys/test")
    print(f"📋 Available Surveys: http://127.0.0.1:5000/api/surveys/available")
    print(f"📊 Dashboard API: http://127.0.0.1:5000/api/dashboard/overview")  # NEU!
    print("=" * 50)
    
    # Start the application
    app.run(host='127.0.0.1', port=5000, debug=True)