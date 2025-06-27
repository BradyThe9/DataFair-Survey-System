#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Reset Script for DataFair Survey System
"""

import os
import sys
from datetime import datetime

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def reset_database():
    """Reset the entire database"""
    print("🔄 Starting database reset...")
    
    # Database path
    instance_path = os.path.join(current_dir, 'instance')
    db_path = os.path.join(instance_path, 'datafair.db')
    
    # Remove existing database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✅ Removed existing database: {db_path}")
        except Exception as e:
            print(f"❌ Error removing database: {e}")
            return False
    else:
        print("ℹ️  No existing database found")
    
    # Import and create new database
    try:
        from app.database import db, init_db
        from app.models import User, Survey, SurveyResponse, DataPermission, Earning
        from config import Config
        from flask import Flask
        
        # Create temporary app for database operations
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Initialize database
        init_db(app)
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ New database tables created")
            
            # Create demo data
            from werkzeug.security import generate_password_hash
            
            # Create demo user
            demo_user = User(
                email='demo@datafair.com',
                password_hash=generate_password_hash('demo123'),
                first_name='Demo',
                last_name='User',
                is_verified=True
            )
            db.session.add(demo_user)
            
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
            
            # Commit all changes
            db.session.commit()
            
            print("✅ Demo user created: demo@datafair.com / demo123")
            print("✅ Sample surveys created")
            
        print("=" * 50)
        print("🎉 Database reset completed successfully!")
        print("📍 You can now start the application with: python app.py")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating new database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("DataFair Survey System - Database Reset")
    print("=" * 50)
    
    # Confirm reset
    response = input("⚠️  This will delete all existing data. Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        success = reset_database()
        if success:
            print("\n✅ Reset completed successfully!")
        else:
            print("\n❌ Reset failed!")
            sys.exit(1)
    else:
        print("🚫 Reset cancelled")
        sys.exit(0)