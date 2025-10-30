# RoshTech Industries - Central CRM

![RoshTech CRM](https://img.shields.io/badge/Status-Development-yellow)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Latest-green)

## 📋 Project Overview

The RoshTech CRM is a comprehensive Customer Relationship Management platform designed to be the central nervous system of RoshTech Industries' business operations. This enterprise-grade solution manages client relationships, streamlines operations, and provides actionable insights across all business divisions.

### Key Features
- 👥 Client Account Management
- 📊 Sales Pipeline Tracking
- 📈 Business Analytics Dashboard
- 🔐 Role-based Access Control
- 📱 Responsive Design
- 🔄 Real-time Updates

### Business Divisions Supported
- 🚀 RoshTech Technologies
- 🚛 RoshTech Logistics
- 🏢 RoshTech Properties

## 🛠️ Technology Stack

### Backend
- **Framework:** Python 3 + Flask
- **Database:** SQLAlchemy with SQLite (Development) / PostgreSQL (Production)
- **Authentication:** Flask-Login
- **API Documentation:** Swagger/OpenAPI

### Frontend
- **UI Framework:** HTML5 + Tailwind CSS
- **JavaScript:** Vanilla JS with Modern ES6+ Features
- **Templating:** Jinja2
- **Icons:** Font Awesome

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SirMphuthi/roshtech-crm.git
   cd roshtech-crm
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   # Windows (PowerShell)
   $env:FLASK_APP = "run.py"

   # macOS/Linux
   export FLASK_APP=run.py
   ```

5. **Initialize Database**
   ```bash
   flask db init
   flask db migrate -m "Initial CRM database structure"
   flask db upgrade
   ```

### Running the Application
```bash
python run.py
```
The application will be available at `http://127.0.0.1:5000`

## 📁 Project Structure
```
roshtech-crm/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   └── templates/
├── requirements.txt
└── run.py
```

## 🔒 Security

- All passwords are hashed using industry-standard algorithms
- CSRF protection enabled
- Regular security audits
- Rate limiting implemented
- Input validation and sanitization

## 🤝 Contributing

1. Create a feature branch
2. Commit your changes
3. Push to the branch
4. Create a Pull Request

## ✅ Running tests

Quick commands to run the test-suite locally.

PowerShell (Windows):
```powershell
# ensure the repo root is on PYTHONPATH for tests
$env:PYTHONPATH = "."
pytest -q
```

macOS / Linux:
```bash
export PYTHONPATH=. ; pytest -q
```

To run a single test file or test case, use the pytest -k or pass the path to a file:
```bash
pytest tests/test_users.py::test_create_user -q
```

## 🧰 Developer notes

- The app uses Flask + Flask-Login for auth. Tests create an `admin@test.com` user during setup.
- If you need to switch the test client between users in tests, the test auth helper now logs out before logging in to ensure a clean session.
- Database migrations are managed with Alembic/Flask-Migrate. Generate migrations with `flask db migrate` and apply with `flask db upgrade`.
- There are a handful of deprecation warnings from SQLAlchemy about `Query.get()` — consider migrating to `Session.get()` in a follow-up.

## � CSRF protection (recommended)

This app supports optional CSRF protection via Flask-WTF. CSRF will be enabled at runtime if `flask-wtf` is installed and configured.

To enable CSRF in your environment:

PowerShell:
```powershell
pip install Flask-WTF
$env:FLASK_APP = "run.py"
flask run
```

If CSRF is enabled, the layout template will include a `meta[name="csrf-token"]` tag and the frontend JS will send this token in the `X-CSRFToken` header for AJAX POST requests.

Tests run with CSRF disabled by default via test config (see `tests/conftest.py`).

## �📝 License

© 2025 RoshTech Industries. All Rights Reserved.

---
Built with ❤️ by the RoshTech Development Team