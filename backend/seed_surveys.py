import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import Survey, SurveyQuestion, SurveyQuestionOption
from datetime import datetime, timedelta

def seed_surveys():
    """Seed the database with sample surveys"""
    app = create_app()
    
    with app.app_context():
        # Lösche existierende Umfragen (optional)
        print("Clearing existing surveys...")
        Survey.query.delete()
        db.session.commit()
        
        print("Creating sample surveys...")
        
        # Umfrage 1: Online-Shopping-Verhalten
        survey1 = Survey(
            title="Online-Shopping-Gewohnheiten 2025",
            description="Teile deine Erfahrungen und Präferenzen beim Online-Shopping mit uns.",
            company="E-Commerce Insights GmbH",
            reward=3.50,
            estimated_time=10,
            category="E-Commerce",
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(survey1)
        db.session.flush()
        
        # Fragen für Umfrage 1
        q1_1 = SurveyQuestion(
            survey_id=survey1.id,
            question_text="Wie oft kaufst du online ein?",
            question_type="single",
            order=1,
            required=True
        )
        db.session.add(q1_1)
        db.session.flush()
        
        # Optionen für Frage 1
        options = [
            "Täglich",
            "Mehrmals pro Woche",
            "Einmal pro Woche",
            "Mehrmals pro Monat",
            "Einmal pro Monat oder seltener"
        ]
        for i, opt in enumerate(options):
            db.session.add(SurveyQuestionOption(
                question_id=q1_1.id,
                option_text=opt,
                order=i+1
            ))
        
        q1_2 = SurveyQuestion(
            survey_id=survey1.id,
            question_text="Welche Produktkategorien kaufst du am häufigsten online? (Mehrfachauswahl möglich)",
            question_type="multiple",
            order=2,
            required=True
        )
        db.session.add(q1_2)
        db.session.flush()
        
        categories = [
            "Kleidung & Mode",
            "Elektronik & Technik",
            "Bücher & Medien",
            "Lebensmittel",
            "Haushaltswaren",
            "Beauty & Pflege",
            "Sport & Freizeit"
        ]
        for i, cat in enumerate(categories):
            db.session.add(SurveyQuestionOption(
                question_id=q1_2.id,
                option_text=cat,
                order=i+1
            ))
        
        q1_3 = SurveyQuestion(
            survey_id=survey1.id,
            question_text="Was ist dir beim Online-Shopping am wichtigsten?",
            question_type="scale",
            order=3,
            required=True
        )
        db.session.add(q1_3)
        
        q1_4 = SurveyQuestion(
            survey_id=survey1.id,
            question_text="Gibt es etwas, das dich vom Online-Shopping abhält? Bitte erkläre kurz.",
            question_type="text",
            order=4,
            required=False
        )
        db.session.add(q1_4)
        
        # Umfrage 2: Streaming-Dienste
        survey2 = Survey(
            title="Streaming-Dienste Nutzungsverhalten",
            description="Hilf uns zu verstehen, wie du Streaming-Dienste nutzt.",
            company="MediaTrends Analytics",
            reward=2.80,
            estimated_time=8,
            category="Entertainment",
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=45)
        )
        db.session.add(survey2)
        db.session.flush()
        
        q2_1 = SurveyQuestion(
            survey_id=survey2.id,
            question_text="Welche Streaming-Dienste nutzt du? (Mehrfachauswahl möglich)",
            question_type="multiple",
            order=1,
            required=True
        )
        db.session.add(q2_1)
        db.session.flush()
        
        streaming_services = [
            "Netflix",
            "Amazon Prime Video",
            "Disney+",
            "Apple TV+",
            "Spotify",
            "YouTube Premium",
            "Andere"
        ]
        for i, service in enumerate(streaming_services):
            db.session.add(SurveyQuestionOption(
                question_id=q2_1.id,
                option_text=service,
                order=i+1
            ))
        
        q2_2 = SurveyQuestion(
            survey_id=survey2.id,
            question_text="Wie viele Stunden pro Woche nutzt du Streaming-Dienste?",
            question_type="single",
            order=2,
            required=True
        )
        db.session.add(q2_2)
        db.session.flush()
        
        hours_options = [
            "Weniger als 5 Stunden",
            "5-10 Stunden",
            "10-20 Stunden",
            "20-30 Stunden",
            "Mehr als 30 Stunden"
        ]
        for i, opt in enumerate(hours_options):
            db.session.add(SurveyQuestionOption(
                question_id=q2_2.id,
                option_text=opt,
                order=i+1
            ))
        
        # Umfrage 3: Nachhaltigkeit im Alltag
        survey3 = Survey(
            title="Nachhaltigkeit und Umweltbewusstsein",
            description="Teile deine Einstellung und Praktiken zum Thema Nachhaltigkeit.",
            company="Green Future Research",
            reward=4.20,
            estimated_time=12,
            category="Lifestyle",
            status="active"
        )
        db.session.add(survey3)
        db.session.flush()
        
        q3_1 = SurveyQuestion(
            survey_id=survey3.id,
            question_text="Wie wichtig ist dir Nachhaltigkeit im Alltag?",
            question_type="scale",
            order=1,
            required=True
        )
        db.session.add(q3_1)
        
        q3_2 = SurveyQuestion(
            survey_id=survey3.id,
            question_text="Welche nachhaltigen Praktiken verfolgst du? (Mehrfachauswahl möglich)",
            question_type="multiple",
            order=2,
            required=True
        )
        db.session.add(q3_2)
        db.session.flush()
        
        practices = [
            "Mülltrennung",
            "Plastik vermeiden",
            "Öffentliche Verkehrsmittel nutzen",
            "Regional einkaufen",
            "Second-Hand kaufen",
            "Energie sparen",
            "Vegetarisch/Vegan leben"
        ]
        for i, practice in enumerate(practices):
            db.session.add(SurveyQuestionOption(
                question_id=q3_2.id,
                option_text=practice,
                order=i+1
            ))
        
        q3_3 = SurveyQuestion(
            survey_id=survey3.id,
            question_text="Was hält dich davon ab, nachhaltiger zu leben?",
            question_type="text",
            order=3,
            required=False
        )
        db.session.add(q3_3)
        
        # Umfrage 4: Fitness und Gesundheit
        survey4 = Survey(
            title="Fitness-Tracker und Gesundheits-Apps",
            description="Wie nutzt du Technologie für deine Gesundheit?",
            company="HealthTech Solutions",
            reward=3.00,
            estimated_time=7,
            category="Gesundheit",
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=20)
        )
        db.session.add(survey4)
        db.session.flush()
        
        q4_1 = SurveyQuestion(
            survey_id=survey4.id,
            question_text="Nutzt du einen Fitness-Tracker oder eine Smartwatch?",
            question_type="single",
            order=1,
            required=True
        )
        db.session.add(q4_1)
        db.session.flush()
        
        db.session.add(SurveyQuestionOption(question_id=q4_1.id, option_text="Ja", order=1))
        db.session.add(SurveyQuestionOption(question_id=q4_1.id, option_text="Nein", order=2))
        db.session.add(SurveyQuestionOption(question_id=q4_1.id, option_text="Plane die Anschaffung", order=3))
        
        q4_2 = SurveyQuestion(
            survey_id=survey4.id,
            question_text="Welche Gesundheitsdaten trackst du? (Mehrfachauswahl möglich)",
            question_type="multiple",
            order=2,
            required=False
        )
        db.session.add(q4_2)
        db.session.flush()
        
        health_data = [
            "Schritte",
            "Herzfrequenz",
            "Schlaf",
            "Kalorien",
            "Workouts",
            "Gewicht",
            "Nichts davon"
        ]
        for i, data in enumerate(health_data):
            db.session.add(SurveyQuestionOption(
                question_id=q4_2.id,
                option_text=data,
                order=i+1
            ))
        
        # Umfrage 5: Home Office Erfahrungen
        survey5 = Survey(
            title="Home Office und Remote Work",
            description="Deine Erfahrungen mit dem Arbeiten von zu Hause.",
            company="WorkLife Balance Institute",
            reward=5.00,
            estimated_time=15,
            category="Arbeit",
            status="active"
        )
        db.session.add(survey5)
        db.session.flush()
        
        q5_1 = SurveyQuestion(
            survey_id=survey5.id,
            question_text="Wie oft arbeitest du im Home Office?",
            question_type="single",
            order=1,
            required=True
        )
        db.session.add(q5_1)
        db.session.flush()
        
        home_office_frequency = [
            "Vollzeit Remote",
            "3-4 Tage pro Woche",
            "1-2 Tage pro Woche",
            "Gelegentlich",
            "Nie"
        ]
        for i, freq in enumerate(home_office_frequency):
            db.session.add(SurveyQuestionOption(
                question_id=q5_1.id,
                option_text=freq,
                order=i+1
            ))
        
        q5_2 = SurveyQuestion(
            survey_id=survey5.id,
            question_text="Wie zufrieden bist du mit deiner Home Office Situation?",
            question_type="scale",
            order=2,
            required=True
        )
        db.session.add(q5_2)
        
        q5_3 = SurveyQuestion(
            survey_id=survey5.id,
            question_text="Was sind die größten Herausforderungen im Home Office?",
            question_type="text",
            order=3,
            required=False
        )
        db.session.add(q5_3)
        
        # Commit all changes
        db.session.commit()
        
        print(f"Successfully created {Survey.query.count()} surveys!")
        print("Surveys seeded successfully!")

if __name__ == '__main__':
    seed_surveys()