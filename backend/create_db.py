from app import create_app
from app.database import db

app = create_app()
with app.app_context():
    # Drop all tables first (optional - only for fresh start)
    # db.drop_all()
    
    # Create all tables
    db.create_all()
    print("Database created successfully!")
    
    # Seed initial data
    print("\nSeeding data types...")
    import seed_data
    seed_data.seed_data_types()
    
    print("\nSeeding surveys...")
    import seed_surveys
    seed_surveys.seed_surveys()
    
    print("\nAll done! Database is ready.")