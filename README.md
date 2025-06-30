# DataFair - Deine Daten. Dein Wert. 💰

**Bereinigte Version** - Fair compensation platform for personal data sharing.

DataFair ist eine innovative Plattform, die es Nutzern ermöglicht, fair für ihre Daten entlohnt zu werden. Unternehmen erhalten ethisch beschaffte, hochqualitative Daten für Marktforschung und Analytics.

## 🏗️ Projektstruktur (bereinigt)

```
DataFair/
├── backend/                    # Flask Backend
│   ├── app/
│   │   ├── routes/            # API Routes (bereinigt)
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── api.py         # General API
│   │   │   ├── surveys.py     # Survey System
│   │   │   ├── dashboard_routes.py  # Dashboard API
│   │   │   ├── data_routes.py # Data Permissions
│   │   │   ├── earning_routes.py    # Earnings & Payouts
│   │   │   └── user_routes.py # User Management
│   │   ├── models.py          # Database Models
│   │   ├── database.py        # DB Configuration
│   │   └── __init__.py
│   ├── app.py                 # Main Application (bereinigt)
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python Dependencies
│   ├── seed_surveys.py        # Sample Data
│   └── instance/              # SQLite Database
├── frontend/                   # Frontend Files
│   ├── pages/                 # HTML Pages
│   │   ├── index.html         # Landing Page
│   │   ├── login.html         # Login
│   │   ├── register.html      # Registration
│   │   ├── dashboard.html     # User Dashboard
│   │   └── enterprise.html    # B2B Page
│   └── assets/
│       └── js/
│           └── api.js         # Frontend API Client
├── package.json               # Node.js Config (repariert)
├── README.md                  # Diese Datei
└── .gitignore                 # Git Ignore Rules
```

## 🛠️ Tech Stack

### Backend
- **Flask** - Python Web Framework
- **SQLAlchemy** - ORM für Datenbankoperationen
- **Flask-Login** - Benutzer-Authentifizierung
- **Flask-CORS** - Cross-Origin Resource Sharing
- **SQLite** - Entwicklungsdatenbank

### Frontend
- **HTML5/CSS3/JavaScript** - Basis-Webtechnologien
- **Tailwind CSS** - Utility-First CSS (via CDN)
- **Alpine.js** - Leichtgewichtiges JavaScript Framework (via CDN)
- **Chart.js** - Datenvisualisierung (via CDN)

## 🚀 Quick Start

### 1. Repository klonen
```bash
git clone <repository-url>
cd DataFair
```

### 2. Python Virtual Environment
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

### 4. Anwendung starten
```bash
python app.py
```

**Ausgabe:**
```
🚀 Starting DataFair Application...
✅ Database tables created/verified
✅ Demo user already exists!
✅ 5 surveys already exist
🎉 DataFair Application Ready!
📍 URL: http://127.0.0.1:5000
👤 Demo Login: demo@datafair.com / demo123
```

## 🎯 Features (implementiert)

### ✅ Für Endnutzer
- **User Authentication** - Login/Register/Profile
- **Dashboard** - Verdienst-Übersicht mit Charts
- **Data Management** - Datenfreigaben kontrollieren
- **Survey System** - Umfragen für zusätzliche Einnahmen
- **Activity Feed** - Transparente Datennutzung
- **Test Earnings** - Demo-Verdienste generieren

### ✅ Für Entwickler
- **RESTful API** - Vollständige Backend-API
- **Real-time Dashboard** - Live-Updates via AJAX
- **Responsive Design** - Mobile-optimiert
- **Error Handling** - Graceful Fehlerbehandlung
- **CORS Support** - Frontend-Backend Integration

### 🚧 In Entwicklung
- **Payment Integration** - PayPal/Stripe
- **Email System** - Notifications
- **Enterprise API** - B2B Data Access
- **Admin Panel** - Survey Management

## 🔐 Demo-Zugang

**E-Mail:** `demo@datafair.com`  
**Passwort:** `demo123`

## 📡 API Endpoints

### Authentication
- `POST /auth/login` - User Login
- `POST /auth/logout` - User Logout
- `POST /auth/register` - User Registration
- `GET /auth/profile` - Get Profile

### Dashboard
- `GET /api/dashboard/overview` - Complete Dashboard Data
- `POST /api/dashboard/quick-actions` - Quick Actions

### Data Management
- `GET /api/data-types` - Available Data Types
- `POST /api/data-permissions` - Update Permissions

### Surveys
- `GET /api/surveys/available` - Available Surveys
- `POST /api/surveys/{id}/start` - Start Survey
- `POST /api/surveys/{id}/submit` - Submit Survey

### Earnings
- `GET /api/earnings` - Get Earnings
- `POST /api/payout` - Request Payout

## 🧪 Testing

```bash
# Health Check
curl http://localhost:5000/health

# API Info
curl http://localhost:5000/api

# Login Test
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@datafair.com","password":"demo123"}'
```

## 🧹 Project Cleanup

Das Projekt wurde bereinigt von:
- ❌ Redundanten Dateien (`app_minimal.py`, `run.py`)
- ❌ Leeren Dateien (`main.css`, `components.css`)
- ❌ Unnötigen Routes (`enterprise_routes.py`, `payment_routes.py`)
- ✅ Verbesserte Struktur und klarere Imports

## 🐛 Troubleshooting

### Problem: 404 bei HTML-Seiten
**Lösung:** Verwende `python app.py` (nicht `flask run`)

### Problem: Login funktioniert nicht
**Lösung:** Prüfe Demo-User in Console-Output

### Problem: Dashboard zeigt keine Daten
**Lösung:** Drücke "Test-Verdienste generieren" Button

## 📈 Development Roadmap

### Phase 1: Core Features (✅ Abgeschlossen)
- User Authentication
- Basic Dashboard
- Data Type Management
- Survey System

### Phase 2: Earnings System (🚧 In Arbeit)
- Real Earnings Logic
- Payout System
- Payment Integration

### Phase 3: Enterprise Features (📅 Geplant)
- Company API
- Data Analytics
- Admin Panel
- Billing System

### Phase 4: Production (📅 Geplant)
- Email System
- Performance Optimization
- Security Hardening
- Deployment Guide

## 🤝 Contributing

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Committe deine Änderungen
4. Push zum Branch
5. Öffne einen Pull Request

## 📝 License

MIT License - siehe [LICENSE](LICENSE) für Details.

## 📞 Support

- **Issues:** GitHub Issues verwenden
- **Email:** support@datafair.com
- **Documentation:** Siehe `/docs` (coming soon)

---

**Made with ❤️ for fair data economy**  
*Version 1.0.0 - Cleaned & Optimized*