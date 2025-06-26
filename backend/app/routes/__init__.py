# backend/app/routes/__init__.py
# Temporär alle anderen Imports auskommentiert
# from app.routes.auth_routes import auth_bp
# from app.routes.user_routes import user_bp  
# from app.routes.data_routes import data_bp
# from app.routes.earning_routes import earning_bp
# from app.routes.payment_routes import payment_bp
# from app.routes.activity_routes import activity_bp
# from app.routes.enterprise_routes import enterprise_bp

# Nur surveys importieren
from app.routes.surveys import surveys_bp

__all__ = [
    'surveys_bp'
]