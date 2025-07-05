import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# FIXED IMPORT - Verwende direkte Imports statt create_app
from flask import Flask
from app.database import db, init_db
from app.models import DataType
from config import Config
from datetime import datetime

def seed_data_types():
    """Seed the database with initial data types"""
    
    # Create Flask app locally (Fix für create_app Import)
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    
    with app.app_context():
        # Check if data types already exist
        if DataType.query.count() > 0:
            print("Data types already seeded.")
            return
        
        print("Creating data types...")
        
        data_types = [
            {
                'name': 'Shopping-Verhalten',
                'description': 'Online-Einkäufe, besuchte Shops, Produktinteressen',
                'icon': '🛒',
                'monthly_value': 12.00,
                'category': 'E-Commerce'
            },
            {
                'name': 'Demografische Daten',
                'description': 'Alter, Geschlecht, Wohnort, Familienstand',
                'icon': '👤',
                'monthly_value': 8.50,
                'category': 'Persönlich'
            },
            {
                'name': 'Interessensbereiche',
                'description': 'Hobbys, Sport, Reisen, Entertainment-Präferenzen',
                'icon': '🎯',
                'monthly_value': 6.75,
                'category': 'Lifestyle'
            },
            {
                'name': 'Technologie-Nutzung',
                'description': 'Geräte, Apps, Software-Präferenzen',
                'icon': '📱',
                'monthly_value': 5.25,
                'category': 'Technologie'
            },
            {
                'name': 'Fitness & Gesundheit',
                'description': 'Aktivitätsdaten, Gesundheitsinteressen (anonymisiert)',
                'icon': '💪',
                'monthly_value': 9.00,
                'category': 'Gesundheit'
            },
            {
                'name': 'Finanzverhalten',
                'description': 'Ausgabenkategorien, Spar- und Investitionsinteressen',
                'icon': '💰',
                'monthly_value': 15.50,
                'category': 'Finanzen'
            }
        ]
        
        for dt_data in data_types:
            data_type = DataType(**dt_data)
            db.session.add(data_type)
        
        db.session.commit()
        print(f"Successfully created {len(data_types)} data types!")

if __name__ == '__main__':
    seed_data_types()