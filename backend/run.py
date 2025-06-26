"""
DataFair Backend - Hauptstartpunkt
"""
from app import create_app
import os

# App-Instanz erstellen
app = create_app()

if __name__ == '__main__':
    # Entwicklungsserver starten
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True  # Nur für Entwicklung!
    )
