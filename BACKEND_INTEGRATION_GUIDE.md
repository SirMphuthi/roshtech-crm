# Backend Integration Setup Guide

This guide walks you through setting up the complete RoshTech CRM with backend and frontend integration.

## Prerequisites

- Python 3.8+
- Node.js 18+ (already installed)
- Flask and dependencies (in `requirements.txt`)
- React and npm dependencies (in `public/package.json`)

## Step 1: Install Backend Dependencies

```powershell
# From project root
pip install -r requirements.txt
```

Ensure Flask-CORS is included (added to requirements.txt).

## Step 2: Create Test Admin User

```powershell
# From project root
python scripts/create_test_admin.py
```

This will output your test credentials:
```
Admin Account:
  Email:    admin@roshtech.com
  Password: password123
  Role:     owner

Test Account:
  Email:    testuser@roshtech.com
  Password: password123
  Role:     sales
```

## Step 3: Start Flask Backend Server

```powershell
# From project root
python run.py
```

The Flask server will start at `http://localhost:5000`.

**API Endpoints Available:**

### Authentication
- `POST /api/auth/login` - Login with email & password
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### Accounts (CRUD)
- `GET /api/accounts` - List accounts
- `POST /api/accounts` - Create account
- `GET /api/accounts/<id>` - Get single account
- `PUT /api/accounts/<id>` - Update account
- `DELETE /api/accounts/<id>` - Delete account

### Contacts (CRUD)
- `GET /api/contacts` - List contacts
- `POST /api/contacts` - Create contact
- `GET /api/contacts/<id>` - Get single contact
- `PUT /api/contacts/<id>` - Update contact
- `DELETE /api/contacts/<id>` - Delete contact

### Opportunities (CRUD)
- `GET /api/opportunities` - List opportunities
- `POST /api/opportunities` - Create opportunity
- `GET /api/opportunities/<id>` - Get single opportunity
- `PUT /api/opportunities/<id>` - Update opportunity
- `DELETE /api/opportunities/<id>` - Delete opportunity

### Leads (same as Opportunities)
- `GET /api/leads` - List leads
- `POST /api/leads` - Create lead
- `GET /api/leads/<id>` - Get single lead
- `PUT /api/leads/<id>` - Update lead
- `DELETE /api/leads/<id>` - Delete lead

### Tasks & Reports (placeholder)
- `GET /api/tasks` - List tasks (not implemented)
- `GET /api/reports` - List reports (not implemented)

## Step 4: Start React Frontend

In a **new terminal** (keep Flask running):

```powershell
cd public
npm start
```

The React app will open at `http://localhost:3000`.

## Step 5: Test the Integration

1. Open `http://localhost:3000` in your browser
2. You'll see the login page with test credentials displayed
3. Login with:
   - **Email:** `admin@roshtech.com`
   - **Password:** `password123`
4. You should be redirected to the dashboard
5. Dashboard should display stats from the backend

## Frontend Integration

### API Client

The React frontend uses a centralized API client at `src/services/api.js`. It handles:
- Base URL configuration
- Authentication headers
- CORS credentials
- Error handling (401 redirects to login)

### Usage in React Components

```javascript
import api from '../services/api';

// Login
const response = await api.login(email, password);

// Get accounts
const accounts = await api.getAccounts(page, query);

// Create account
const newAccount = await api.createAccount({ name, industry, phone, website });

// Update account
await api.updateAccount(accountId, { name: 'New Name' });

// Delete account
await api.deleteAccount(accountId);
```

### Page Integration Status

- ✅ LoginPage - Integrated with backend
- ⏳ DashboardPage - Ready for data binding (see DashboardPage.js for example)
- ⏳ AccountsPage - Ready for integration
- ⏳ ContactsPage - Ready for integration
- ⏳ LeadsPage - Ready for integration
- ⏳ OpportunitiesPage - Ready for integration
- ⏳ TasksPage - Not yet implemented (placeholder)
- ⏳ ReportsPage - Not yet implemented (placeholder)

## CORS Configuration

The Flask backend is configured with CORS enabled for:
- `http://localhost:3000` (React dev server)
- `http://localhost:5000` (Flask dev server)

Cookies and credentials are supported for session management.

## Database

The app uses SQLite by default (database file: `app.db`). To reset the database:

```powershell
# Delete the existing database
Remove-Item app.db

# Re-run Flask to recreate it
python run.py

# Create test admin again
python scripts/create_test_admin.py
```

## Troubleshooting

### "Cannot reach backend" error
- Make sure Flask server is running on `http://localhost:5000`
- Check that CORS is enabled in `app/__init__.py`
- Verify Flask-CORS is installed: `pip install Flask-CORS`

### "401 Unauthorized" on protected endpoints
- Ensure you're logged in and have a valid session cookie
- Check that credentials match the test admin user created

### "Module not found" errors in React
- Run `npm install` in the `public` folder if you haven't yet
- Clear npm cache: `npm cache clean --force`

### Database errors
- Delete `app.db` and restart Flask to recreate it
- Run `python scripts/create_test_admin.py` to recreate test users

## Next Steps

1. **Complete page integrations** - Update each page (Accounts, Contacts, Leads, etc.) to fetch and display data from backend using the API client
2. **Add CRUD modals** - Create modals for adding/editing/deleting records
3. **Implement Tasks** - Add Task model and endpoints
4. **Add Reports** - Implement reporting endpoints and dashboard
5. **Deploy** - Set up production database and deployment pipeline

## Quick Reference: Test Credentials

```
Admin:
  Email: admin@roshtech.com
  Password: password123

Test User:
  Email: testuser@roshtech.com
  Password: password123
```

---

**For questions or issues, check the Flask backend logs (`http://localhost:5000`) and React console (`F12` in browser).**
