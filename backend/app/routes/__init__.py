from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.data_routes import data_bp
from app.routes.earning_routes import earning_bp
from app.routes.survey_routes import survey_bp

__all__ = ['auth_bp', 'user_bp', 'data_bp', 'earning_bp', 'survey_bp']