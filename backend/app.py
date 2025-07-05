#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataFair - Main Application
Mit korrigierten Frontend-Routes und DataType Seeding
"""

import os
import sys
from datetime import datetime
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import our modules
from app.database import db, init_db
from app.models import User, Survey
from config import Config

def create_app():
    """Application Factory Pattern"""
    
    # Bestimme die korrekten Pfade
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    frontend_dir = os.path.join(project_root, 'frontend')
    pages_dir = os.path.join(frontend_dir, 'pages')
    assets_dir = os.path.join(frontend_dir, 'assets')
    
    print(f"Backend dir: {backend_dir}")
    print(f"Frontend dir: {frontend_dir}")
    print(f"Pages dir: {pages_dir}")
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize database
    init_db(app)
    
    # CORS Configuration
    CORS(app, 
         origins=["http://localhost:5000", "http://127.0.0.1:5000"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Flask-Login Configuration
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bitte melde dich an, um auf diese Seite zuzugreifen.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register Core Blueprints (funktionieren garantiert)
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp  
    from app.routes.surveys import surveys_bp
    from app.routes.dashboard_routes import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(surveys_bp, url_prefix='/api/surveys')
    app.register_blueprint(dashboard_bp)  # Has own prefix
    
    # Optional Blueprints (nur registrieren wenn sie funktionieren)
    try:
        from app.routes.data_routes import data_bp
        app.register_blueprint(data_bp, url_prefix='/api')
        print("✅ Data routes loaded")
    except ImportError as e:
        print(f"⚠️  Data routes skipped: {e}")
    
    try:
        from app.routes.earning_routes import earning_bp
        app.register_blueprint(earning_bp, url_prefix='/api')
        print("✅ Earning routes loaded")
    except ImportError as e:
        print(f"⚠️  Earning routes skipped: {e}")
    
    try:
        from app.routes.user_routes import user_bp
        app.register_blueprint(user_bp, url_prefix='/api')
        print("✅ User routes loaded")
    except ImportError as e:
        print(f"⚠️  User routes skipped: {e}")
    
    # =========================
    # FRONTEND ROUTES (KORRIGIERT)
    # =========================
    
    @app.route('/')
    def index():
        """Startseite"""
        print(f"📍 Serving index from: {pages_dir}")
        return send_from_directory(pages_dir, 'index.html')
    
    # Explizite HTML-Routes
    @app.route('/index.html')
    def index_alt():
        return send_from_directory(pages_dir, 'index.html')
    
    @app.route('/login.html')
    def login_page():
        return send_from_directory(pages_dir, 'login.html')
    
    @app.route('/register.html')
    def register_page():
        return send_from_directory(pages_dir, 'register.html')
    
    @app.route('/dashboard.html')
    def dashboard_page():
        return send_from_directory(pages_dir, 'dashboard.html')
    
    @app.route('/enterprise.html')
    def enterprise_page():
        return send_from_directory(pages_dir, 'enterprise.html')
    
    # Legacy /pages/ routes (falls irgendwo noch verlinkt)
    @app.route('/pages/<filename>')
    def serve_pages_legacy(filename):
        print(f"📄 Legacy page request: {filename}")
        return send_from_directory(pages_dir, filename)
    
    # Assets
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        print(f"🎨 Asset request: {filename}")
        return send_from_directory(assets_dir, filename)
    
    # Frontend assets (alternative path)
    @app.route('/frontend/assets/<path:filename>')
    def serve_frontend_assets(filename):
        return send_from_directory(assets_dir, filename)
    
    # Favicon
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(assets_dir, 'favicon.ico')
    
    # =========================
    # API ROUTES
    # =========================
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'paths': {
                'frontend_dir': frontend_dir,
                'pages_dir': pages_dir,
                'assets_dir': assets_dir
            },
            'features': {
                'auth': True,
                'surveys': True,
                'dashboard': True,
                'earnings': 'partial',
                'data_permissions': 'active'  # JETZT AKTIV!
            }
        })
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'name': 'DataFair API',
            'version': '1.0.0',
            'description': 'Fair compensation for personal data',
            'endpoints': {
                'auth': '/auth/',
                'api': '/api/',
                'surveys': '/api/surveys/',
                'dashboard': '/api/dashboard/',
                'health': '/health'
            }
        })
    
    # Debug: Liste alle verfügbaren Routen
    @app.route('/debug/routes')
    def debug_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        return jsonify({'routes': routes})
    
    # =========================
    # ERROR HANDLERS
    # =========================
    
    @app.errorhandler(404)
    def not_found(error):
        print(f"❌ 404 Error: {error}")
        return jsonify({'error': 'Not found', 'path': str(error)}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        print(f"❌ 500 Error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

def create_demo_data():
    """Create demo user and sample data"""
    print("Checking for demo user...")
    
    # Check if demo user exists
    demo_user = User.query.filter_by(email='demo@datafair.com').first()
    
    if not demo_user:
        demo_user = User(
            email='demo@datafair.com',
            password_hash=generate_password_hash('demo123'),
            first_name='Demo',
            last_name='User',
            is_verified=True
        )
        db.session.add(demo_user)
        print("✅ Demo user created: demo@datafair.com / demo123")
    else:
        print("✅ Demo user already exists!")
    
    # Check for DataTypes - NEU!
    from app.models import DataType
    datatype_count = DataType.query.count()
    if datatype_count == 0:
        try:
            from seed_data import seed_data_types
            seed_data_types()
            print("✅ DataTypes seeded!")
        except ImportError as e:
            print(f"⚠️ DataType seeding failed: {e}")
    else:
        print(f"✅ {datatype_count} DataTypes already exist")
    
    # Check for surveys
    survey_count = Survey.query.count()
    if survey_count == 0:
        # Import and run survey seeding
        try:
            from seed_surveys import seed_surveys
            seed_surveys()
            print("✅ Sample surveys created!")
        except ImportError:
            print("⚠️ Survey seeding not available")
    else:
        print(f"✅ {survey_count} surveys already exist")
    
    db.session.commit()

if __name__ == '__main__':
    print("🚀 Starting DataFair Application...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    # Initialize database and demo data
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
        create_demo_data()
    
    print("=" * 50)
    print("🎉 DataFair Application Ready!")
    print(f"📍 URL: http://127.0.0.1:5000")
    print(f"👤 Demo Login: demo@datafair.com / demo123") 
    print(f"📊 Dashboard: http://127.0.0.1:5000/dashboard.html")
    print(f"🧪 Health Check: http://127.0.0.1:5000/health")
    print(f"🔧 Debug Routes: http://127.0.0.1:5000/debug/routes")
    print("=" * 50)
    
    # Start the application
    app.run(host='127.0.0.1', port=5000, debug=True)