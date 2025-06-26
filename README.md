# DataFair - Deine Daten. Dein Wert. 💰

DataFair ist eine innovative Plattform, die es Nutzern ermöglicht, fair für ihre Daten entlohnt zu werden. Unternehmen erhalten ethisch beschaffte, hochqualitative Daten für Marktforschung und Analytics.

## 🏗️ Projektstruktur

```
Yuur/
├── backend/                 # Flask-Backend
│   ├── app/
│   │   ├── routes/         # API-Routen
│   │   ├── models.py       # Datenbankmodelle
│   │   └── database.py     # Datenbank-Konfiguration
│   ├── instance/           # SQLite-Datenbank
│   ├── app.py             # Haupt-Flask-App
│   ├── config.py          # Konfiguration
│   └── requirements.txt   # Python-Dependencies
├── frontend/               # Frontend-Dateien
│   ├── pages/             # HTML-Seiten
│   │   ├── index.html     # Startseite
│   │   ├── login.html     # Login-Seite
│   │   ├── register.html  # Registrierung
│   │   ├── dashboard.html # User-Dashboard
│   │   └── enterprise.html # B2B-Seite
│   └── assets/            # CSS, JS, Bilder
│       └── js/
│           └── api.js     # Frontend-API-Client
├── docs/                  # Dokumentation
├── legal/                 # Rechtliche Dokumente
└── venv/                  # Python Virtual Environment
```

## 🛠️ Technologie-Stack

### Backend
- **Flask** - Python Web Framework
- **SQLAlchemy** - ORM für Datenbankoperationen
- **Flask-Login** - Benutzer-Authentifizierung
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Werkzeug** - Passwort-Hashing
- **SQLite** - Entwicklungsdatenbank

### Frontend
- **HTML5/CSS3/JavaScript** - Basis-Webtechnologien
- **Tailwind CSS** - Utility-First CSS Framework
- **Alpine.js** - Leichtgewichtiges JavaScript Framework
- **Chart.js** - Datenvisualisierung

## 🚀 Installation & Setup

### 1. Repository klonen
```bash
git clone <repository-url>
cd Yuur
```

### 2. Python Virtual Environment erstellen
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# oder
source venv/bin/activate  # Linux/Mac
```

### 3. Dependencies installieren
```bash
cd backend
pip install -r requirements.txt
```

### 4. Datenbank initialisieren
Die Datenbank wird automatisch beim ersten Start erstellt.

## ▶️ Anwendung starten

### Backend starten
```bash
cd backend
python app.py
```

**Ausgabe:**
```
Checking for demo user...
✅ Demo user already exists!
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Frontend aufrufen
Das Frontend wird automatisch über Flask serviert:
- **Startseite:** http://localhost:5000/
- **Login:** http://localhost:5000/login.html
- **Registrierung:** http://localhost:5000/register.html
- **Dashboard:** http://localhost:5000/dashboard.html
- **Enterprise:** http://localhost:5000/enterprise.html

## 🔐 Demo-Zugang

Für Tests steht ein Demo-Account zur Verfügung:

- **E-Mail:** `demo@datafair.com`
- **Passwort:** `demo123`

## 📡 API-Endpoints

### Authentifizierung
- `POST /api/register` - Neue Benutzerregistrierung
- `POST /api/login` - Benutzer-Anmeldung
- `POST /api/logout` - Benutzer-Abmeldung

### Benutzer-Daten
- `GET /api/profile` - Benutzerprofil abrufen
- `PUT /api/profile` - Benutzerprofil aktualisieren

### Daten-Management
- `GET /api/data-types` - Verfügbare Datentypen
- `POST /api/data-permissions` - Datenfreigaben verwalten

### Verdienste & Auszahlungen
- `GET /api/earnings` - Verdienste abrufen
- `POST /api/payout` - Auszahlung beantragen
- `GET /api/payouts` - Auszahlungshistorie

### Umfragen
- `GET /api/surveys` - Verfügbare Umfragen
- `POST /api/surveys/{id}/start` - Umfrage starten
- `POST /api/surveys/{id}/submit` - Umfrage abschließen

## 🎯 Hauptfunktionen

### Für Endnutzer
- **Kostenlose Registrierung** mit E-Mail-Verifizierung
- **Dashboard** mit Verdienstübersicht
- **Datenfreigabe-Kontrolle** - Nutzer entscheiden selbst
- **Umfragen-System** für zusätzliche Einnahmen
- **Auszahlungssystem** (PayPal, Überweisung, Crypto)
- **Aktivitätsfeed** für Transparenz

### Für Unternehmen
- **API-Zugang** für Datenabfragen
- **Transparente Preisgestaltung**
- **DSGVO-konforme Datensammlung**
- **Real-time Datenstreams**

## 🐛 Troubleshooting

### Problem: 404-Fehler bei HTML-Seiten
**Lösung:** Stelle sicher, dass die spezifischen HTML-Routen in `app.py` vor der generischen Route stehen.

### Problem: Login funktioniert nicht
**Lösungen:**
1. Prüfe ob Demo-User erstellt wurde (siehe Console-Output)
2. Teste API direkt: `curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{"email":"demo@datafair.com","password":"demo123"}'`

### Problem: CORS-Fehler
**Lösung:** Überprüfe CORS-Konfiguration in `app.py` - Origins sollten `http://localhost:5000` enthalten.

### Problem: Datenbank-Fehler
**Lösung:** Lösche `instance/` Ordner und starte App neu für frische DB.

## 🔧 Entwicklung

### Debug-Modus
Flask läuft standardmäßig im Debug-Modus:
- **Auto-Reload** bei Code-Änderungen
- **Detaillierte Fehlermeldungen**
- **Debug-PIN** für Browser-Debugging

### Datenbank-Schema ändern
```bash
cd backend
flask db migrate -m "Beschreibung der Änderung"
flask db upgrade
```

### Neue API-Route hinzufügen
1. Route in entsprechender Datei unter `app/routes/` erstellen
2. Blueprint in `app.py` registrieren
3. Frontend-API-Client in `assets/js/api.js` erweitern

## 📋 Entwicklungsnotizen

### Bereits implementiert ✅
- Benutzer-Authentifizierung (Registration/Login)
- Grundlegendes Dashboard
- Datentypen-Management
- Umfragen-System (Backend)
- Responsive Design

### In Entwicklung 🚧
- Payment-Integration
- E-Mail-Versand
- Erweiterte Analytics
- Admin-Panel

### Geplant 📅
- Mobile App
- Advanced Encryption
- Multi-Language Support
- Enterprise APIs

## 🤝 Mitwirken

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) Datei für Details.

## 📞 Support

Bei Fragen oder Problemen:
- **Issues:** Verwende GitHub Issues
- **E-Mail:** support@datafair.com
- **Documentation:** Siehe `/docs` Ordner

---

**Made with ❤️ for fair data economy**