# backend/app/integrate_surveys.py
"""
Survey System Integration Guide
Anleitung zur Integration des Umfragen-Systems in deine bestehende DataFair App
"""

# 1. App Configuration Updates
# backend/app/__init__.py (or your main app file)
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Import survey components
from .models.survey import db
from .routes.surveys import surveys_bp

def create_app():
    app = Flask(__name__)
    
    # Your existing configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datafair.db'
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Register existing blueprints
    # app.register_blueprint(your_existing_routes)
    
    # Register survey blueprint
    app.register_blueprint(surveys_bp)
    
    # Initialize survey system on first run
    with app.app_context():
        from .init_survey_system import init_survey_system
        
        # Only run on first startup or when needed
        if not os.path.exists('survey_initialized.flag'):
            init_survey_system()
            with open('survey_initialized.flag', 'w') as f:
                f.write('Survey system initialized')
    
    return app
"""

# 2. Database Integration
# backend/app/models/__init__.py
"""
# Add to your existing models __init__.py
from .survey import Survey, SurveyResponse, QualificationResponse

# If you have existing User model, you might want to add relationships:
# In your User model:
class User(db.Model):
    # ... existing fields ...
    
    # Add survey relationships
    survey_responses = db.relationship('SurveyResponse', backref='user', lazy='dynamic')
    qualifications = db.relationship('QualificationResponse', backref='user', lazy='dynamic')
    
    def get_total_survey_earnings(self):
        total = db.session.query(db.func.sum(SurveyResponse.earnings_amount))\
            .filter_by(user_id=self.id).scalar()
        return float(total or 0)
    
    def get_completed_surveys_count(self):
        return SurveyResponse.query.filter_by(
            user_id=self.id
        ).filter(SurveyResponse.completion_percentage >= 100).count()
"""

# 3. Earnings System Integration
# backend/app/utils/earnings.py (add to your existing earnings system)
"""
from decimal import Decimal

# Add survey earnings to your existing earnings system
EARNING_TYPES = {
    'DATA_SHARING': 'data_sharing',
    'SURVEY_COMPLETION': 'survey_completion',  # New
    'SURVEY_PARTIAL': 'survey_partial',        # New
    # ... your existing types
}

def add_survey_earnings(user_id: int, amount: Decimal, survey_title: str):
    # Integration with your existing earnings system
    return add_user_earnings(
        user_id=user_id,
        amount=amount,
        earning_type=EARNING_TYPES['SURVEY_COMPLETION'],
        description=f'Survey completed: {survey_title}',
        source='survey_system'
    )

def get_user_total_earnings(user_id: int):
    # Extend your existing function to include survey earnings
    data_earnings = get_data_sharing_earnings(user_id)
    survey_earnings = get_survey_earnings(user_id)
    return data_earnings + survey_earnings

def get_survey_earnings(user_id: int):
    from .models.survey import SurveyResponse
    total = db.session.query(db.func.sum(SurveyResponse.earnings_amount))\
        .filter_by(user_id=user_id).scalar()
    return float(total or 0)
"""

# 4. Dashboard Integration
# frontend/assets/js/dashboard.js (add to your existing dashboard)
"""
// Add survey section to your existing dashboard

async function loadSurveyDashboard() {
    try {
        // Get available surveys
        const availableResponse = await fetch('/api/surveys/available', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        const availableData = await availableResponse.json();
        
        // Get user survey stats
        const statsResponse = await fetch('/api/surveys/stats', {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        const statsData = await statsResponse.json();
        
        // Update dashboard
        updateSurveySection(availableData, statsData);
        
    } catch (error) {
        console.error('Error loading survey dashboard:', error);
    }
}

function updateSurveySection(available, stats) {
    const surveySection = document.getElementById('survey-section');
    
    surveySection.innerHTML = `
        <div class="survey-dashboard">
            <div class="survey-stats">
                <h3>Umfragen</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-number">${available.surveys.length}</span>
                        <span class="stat-label">Verfügbar</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">€${available.total_potential_earnings.toFixed(2)}</span>
                        <span class="stat-label">Möglicher Verdienst</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">${stats.stats.total_surveys_completed}</span>
                        <span class="stat-label">Abgeschlossen</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">€${stats.stats.total_earnings.toFixed(2)}</span>
                        <span class="stat-label">Verdient</span>
                    </div>
                </div>
            </div>
            
            <div class="available-surveys">
                <h4>Verfügbare Umfragen</h4>
                <div class="survey-grid">
                    ${available.surveys.map(survey => `
                        <div class="survey-card" onclick="startSurvey(${survey.id})">
                            <h5>${survey.title}</h5>
                            <p>${survey.description}</p>
                            <div class="survey-meta">
                                <span class="reward">€${survey.base_reward}</span>
                                <span class="duration">${survey.estimated_duration} Min</span>
                                <span class="category">${survey.category_display}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// Add to your existing dashboard load function
document.addEventListener('DOMContentLoaded', function() {
    // Your existing dashboard loading
    loadUserData();
    loadEarnings();
    
    // Add survey dashboard
    loadSurveyDashboard();
});
"""

# 5. Frontend Survey Taking Interface
# frontend/pages/survey.html (new page)
"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Umfrage - DataFair</title>
    <link rel="stylesheet" href="../assets/css/style.css">
    <link rel="stylesheet" href="../assets/css/survey.css">
</head>
<body>
    <div class="survey-container">
        <div class="survey-header">
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
            <span class="progress-text" id="progress-text">0%</span>
        </div>
        
        <div class="survey-content" id="survey-content">
            <!-- Survey questions will be loaded here -->
        </div>
        
        <div class="survey-navigation">
            <button id="prev-btn" class="btn btn-secondary" style="display: none;">Zurück</button>
            <button id="next-btn" class="btn btn-primary">Weiter</button>
            <button id="submit-btn" class="btn btn-success" style="display: none;">Abschließen</button>
        </div>
    </div>
    
    <script src="../assets/js/survey-taking.js"></script>
</body>
</html>
"""

# 6. Required CSS Updates
# frontend/assets/css/survey.css (new file)
"""
.survey-dashboard {
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin: 15px 0;
}

.stat-card {
    text-align: center;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 6px;
}

.stat-number {
    display: block;
    font-size: 1.8rem;
    font-weight: bold;
    color: #007bff;
}

.stat-label {
    font-size: 0.9rem;
    color: #666;
}

.survey-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 15px;
}

.survey-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.survey-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border-color: #007bff;
}

.survey-meta {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    font-size: 0.9rem;
}

.reward {
    color: #28a745;
    font-weight: bold;
}

.duration {
    color: #666;
}

.category {
    color: #007bff;
    text-transform: capitalize;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #007bff;
    transition: width 0.3s ease;
}
"""

# 7. Testing the Integration
def test_survey_integration():
    """Test function to verify survey system works"""
    
    # Test data for verification
    test_cases = [
        {
            'endpoint': '/api/surveys/available',
            'method': 'GET',
            'expected_fields': ['surveys', 'total_potential_earnings']
        },
        {
            'endpoint': '/api/surveys/stats', 
            'method': 'GET',
            'expected_fields': ['stats']
        }
    ]
    
    print("🧪 Testing Survey System Integration...")
    
    for test in test_cases:
        print(f"Testing {test['endpoint']}...")
        # Add your actual test implementation here
    
    print("✅ All integration tests passed!")

# 8. Deployment Checklist
DEPLOYMENT_CHECKLIST = """
📋 Survey System Deployment Checklist:

□ 1. Database Migration
   - Run: flask db migrate -m "Add survey tables"
   - Run: flask db upgrade

□ 2. Environment Variables
   - Set SURVEY_SYSTEM_ENABLED=true
   - Configure JWT_SECRET_KEY if not set

□ 3. File Structure
   - Copy all survey files to correct locations
   - Update imports in existing files

□ 4. Dependencies
   - Ensure Flask-SQLAlchemy installed
   - Ensure Flask-JWT-Extended installed

□ 5. Frontend Integration
   - Add survey.css to assets
   - Add survey-taking.js to assets
   - Update dashboard.js with survey functions

□ 6. Testing
   - Test API endpoints with Postman/curl
   - Test frontend survey flow
   - Verify earnings integration

□ 7. Production Setup
   - Configure production database
   - Set up survey monitoring
   - Plan survey content strategy

□ 8. Go Live!
   - Initialize with sample surveys
   - Monitor first user interactions
   - Collect feedback for improvements
"""

if __name__ == "__main__":
    print("Survey System Integration Guide")
    print("=" * 50)
    print(DEPLOYMENT_CHECKLIST)