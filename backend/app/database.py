#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Configuration for DataFair Survey System
"""

import os
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    
    # Ensure instance directory exists
    instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Database URI configuration
    database_path = os.path.join(instance_path, 'datafair.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # Initialize the database
    db.init_app(app)
    
    print(f"Database configured: {database_path}")
    
    return db

def create_tables(app):
    """Create all database tables"""
    with app.app_context():
        # Import all models to ensure they're registered
        from .models import User, Survey, SurveyResponse, DataPermission, Earning
        
        # Create all tables
        db.create_all()
        print("All database tables created successfully")

def drop_tables(app):
    """Drop all database tables (use with caution!)"""
    with app.app_context():
        db.drop_all()
        print("All database tables dropped")

def reset_database(app):
    """Reset the entire database"""
    with app.app_context():
        drop_tables(app)
        create_tables(app)
        print("Database reset completed")

def get_db_stats():
    """Get database statistics"""
    try:
        from .models import User, Survey, SurveyResponse
        
        stats = {
            'users': User.query.count(),
            'surveys': Survey.query.count(),
            'active_surveys': Survey.query.filter_by(is_active=True).count(),
            'responses': SurveyResponse.query.count(),
            'completed_responses': SurveyResponse.query.filter_by(is_completed=True).count()
        }
        
        return stats
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return None