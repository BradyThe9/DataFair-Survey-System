from flask import Flask, jsonify
from flask_login import LoginManager
from datetime import datetime, timedelta
import os

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'test-key'
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

# Import ONLY surveys
try:
    from app.routes.surveys import surveys_bp
    app.register_blueprint(surveys_bp)
    SURVEYS_ENABLED = True
    print("✅ Survey system loaded!")
except ImportError as e:
    print(f"❌ Survey import failed: {e}")
    SURVEYS_ENABLED = False

# Health check
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'surveys_enabled': SURVEYS_ENABLED,
        'timestamp': datetime.utcnow().isoformat()
    })

# Demo user creation
def create_demo_user():
    from app.database import db
    from app.models import User
    from werkzeug.security import generate_password_hash
    
    try:
        demo_user = User.query.filter_by(email='demo@datafair.com').first()
        if not demo_user:
            demo_user = User(
                email='demo@datafair.com',
                first_name='Demo',
                last_name='User',
                password_hash=generate_password_hash('demo123')
            )
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Demo user created!")
        else:
            print("✅ Demo user exists!")
    except Exception as e:
        print(f"❌ Demo user error: {e}")

if __name__ == '__main__':
    with app.app_context():
        from app.database import db
        db.create_all()
        create_demo_user()
        print("🚀 Minimal DataFair with Surveys starting...")
        
    app.run(debug=True, port=5000, host='127.0.0.1')
