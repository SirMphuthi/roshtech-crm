
# RoshTech Industries - Central CRM

![RoshTech CRM](https://img.shields.io/badge/Status-Development-yellow)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Latest-green)
![React](https://img.shields.io/badge/Frontend-React-blue)

## 📋 Project Overview

RoshTech CRM is a comprehensive, full-stack Customer Relationship Management platform for RoshTech Industries. The backend is built with Flask (Python), and the frontend is a modern React application. The system supports client management, sales pipeline tracking, analytics dashboards, and secure authentication.

### Key Features
- 👥 Client Account Management
- 📊 Sales Pipeline Tracking
- 📈 Business Analytics Dashboard
- 🔐 Role-based Access Control
- 📱 Responsive React Frontend
- 🔄 Real-time Updates

### Business Divisions Supported
- 🚀 RoshTech Technologies
- 🚛 RoshTech Logistics
- 🏢 RoshTech Properties

## 🛠️ Technology Stack

### Backend

#### Backend Dependencies (see `requirements.txt`)
```
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
Flask-CORS
Flask-WTF
python-dotenv
Werkzeug
pytest
pytest-cov
```

- **Icons:** react-icons
**Framework:** React (create-react-app)
**Routing:** react-router-dom
**Icons:** react-icons
**Drag & Drop:** react-beautiful-dnd
**Charts:** recharts
**CSV Export:** react-csv
**Calendar:** react-big-calendar, date-fns
**Custom Components:** Dashboard, Login, Layout, Sidebar, Contacts, Leads, Opportunities, Tasks, Calendar, Reports, User Management, Settings, etc.

#### Frontend Dependencies (see `public/package.json`)
```
react
react-dom
react-router-dom
react-icons
react-scripts
react-beautiful-dnd
recharts
react-csv
react-big-calendar
date-fns
```
### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Node.js & npm (for React frontend)
- Git

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SirMphuthi/roshtech-crm.git
   cd roshtech-crm
   ```

2. **Set Up Python Backend**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```

3. **Set Up React Frontend**
   ```bash
   cd public
   npm install
   npm start
   ```

4. **Environment Variables**
   - Copy `.env.example` to `.env` and configure as needed.

5. **Database Migrations**
   ```bash
   flask db upgrade
   ```

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**
   ```bash
   cd public
   npm install
   ```

5. **Configure Environment**
   ```bash
   # Windows (PowerShell)
   $env:FLASK_APP = "run.py"

   # macOS/Linux
   export FLASK_APP=run.py
   ```

6. **Initialize Database**
   ```bash
   flask db init
   flask db migrate -m "Initial CRM database structure"
   flask db upgrade
   ```

### Running the Application
**Backend:**
```bash
python run.py --host=0.0.0.0 --port=5000
```
**Frontend:**
```bash
cd public
npm start
```
The backend will be available at `http://localhost:5000`, and the React frontend at `http://localhost:3000`.

## 📁 Project Structure
```
roshtech-crm/
├── app/                # Flask backend
├── public/             # React frontend
├── requirements.txt
├── run.py
└── README.md
```


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

1. **Rate Limiting**
   - API endpoints are rate-limited to prevent abuse
   - Default: 100 requests per hour per IP
   - Token generation: 5 requests per hour
   - Customizable via environment variables

2. **Security Headers**
   - HTTP Strict Transport Security (HSTS)
   - Content Security Policy (CSP)
   - X-Frame-Options
   - X-Content-Type-Options
   - X-XSS-Protection

3. **Session Security**
   - Secure session cookies
   - HTTP-only cookies
   - SameSite cookie policy
   - Configurable session lifetime
   - CSRF protection enabled by default for browser forms

4. **API Security**
   - Token-based authentication
   - Rate limiting per endpoint
   - Input validation and sanitization
   - Role-based access control
   - CORS enabled for frontend-backend integration
   - CSRF protection is **exempted for API endpoints** to support React and external clients

5. **Frontend Security**
   - React frontend communicates securely with backend via CORS
   - Authentication state managed via secure tokens and session



## 🤝 Contributing

1. Create a feature branch
2. Commit your changes
3. Push to the branch
4. Create a Pull Request



## ✅ Running tests

Quick commands to run the backend test-suite locally.

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

Frontend tests can be run with:
```bash
cd public
npm test
```


## 🧰 Developer notes

- The backend uses Flask + Flask-Login for authentication. Tests create an `admin@test.com` user during setup.
- React frontend is fully integrated with backend APIs for login, dashboard, and CRUD operations.
- If you need to switch the test client between users in tests, the test auth helper now logs out before logging in to ensure a clean session.
- Database migrations are managed with Alembic/Flask-Migrate. Generate migrations with `flask db migrate` and apply with `flask db upgrade`.
- All legacy `Query.get()` and `Query.get_or_404()` usages have been migrated to `Session.get()` for SQLAlchemy 2.x compatibility.




## 🔒 CSRF protection

- CSRF protection is enabled by default via Flask-WTF for browser forms.
- **API endpoints are exempted from CSRF protection** to support React and external clients.
- Tests run with CSRF disabled by default via test config (see `tests/conftest.py`).



## 📝 License

© 2025 RoshTech Industries. All Rights Reserved.

---
Built with ❤️ by the RoshTech Development Team