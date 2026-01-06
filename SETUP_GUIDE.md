# Setup Guide - Getting Started

## What We've Built (Phase 1 - Foundation)

### ✅ Completed

1. **Project Structure**: All folders and files organized
2. **Backend API**: Full authentication system with FastAPI
   - User registration
   - Login with JWT tokens
   - Session management
   - Protected endpoints
3. **Database**: PostgreSQL schema with SQLAlchemy models
   - Users, Roles, UserRoles, UserSessions tables
   - Alembic migrations setup
4. **Configuration**: Environment variables and settings management
5. **Security**: Password hashing, JWT tokens, token validation
6. **Documentation**: README and setup instructions

### 📂 File Overview

**Critical Backend Files Created:**
- [backend/app/main.py](backend/app/main.py) - FastAPI application entry point
- [backend/app/config.py](backend/app/config.py) - Configuration management
- [backend/app/models/user.py](backend/app/models/user.py) - Database models
- [backend/app/api/auth.py](backend/app/api/auth.py) - Authentication endpoints
- [backend/app/utils/security.py](backend/app/utils/security.py) - Security utilities
- [backend/requirements.txt](backend/requirements.txt) - Python dependencies
- [scripts/init_db.py](scripts/init_db.py) - Database initialization

## 🚀 How to Start the Backend

### Step 1: Install Prerequisites

1. **Install PostgreSQL 15+**
   - Download: https://www.postgresql.org/download/windows/
   - During installation, remember the postgres user password
   - Port: 5432 (default)

2. **Install Redis (Memurai for Windows)**
   - Download: https://www.memurai.com/get-memurai
   - Install and start the service
   - Verify: Open Command Prompt and run `memurai-cli ping` (should return PONG)

3. **Verify Python and Node.js**
   ```bash
   python --version  # Should be 3.11+
   node --version    # Should be 18+
   ```

### Step 2: Create PostgreSQL Database

Open Command Prompt as Administrator:

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql, run these commands:
CREATE DATABASE tableau_app;
CREATE USER tableau_user WITH PASSWORD 'MySecurePassword123';
GRANT ALL PRIVILEGES ON DATABASE tableau_app TO tableau_user;
\q
```

### Step 3: Set Up Backend

```bash
# Navigate to backend folder
cd c:\Users\sambi\OneDrive\TableauApp\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies (this will take a few minutes)
pip install -r requirements.txt

# Create .env file
copy .env.example .env
```

### Step 4: Edit .env File

Open `backend\.env` in a text editor and update:

```ini
# Change this line with your actual password:
DATABASE_URL=postgresql+asyncpg://tableau_user:MySecurePassword123@localhost/tableau_app

# Generate a random secret key (32+ characters):
SECRET_KEY=your-super-secret-key-change-this-to-something-random-32-chars-min

# Keep other defaults for now
DEBUG=True
HOST=127.0.0.1
PORT=8000
```

### Step 5: Initialize Database

```bash
# Make sure you're in the backend folder with venv activated
python ..\scripts\init_db.py
```

You should see:
```
✓ Database tables created
✓ Created default roles: admin, editor, viewer
✓ Created admin user (username: admin, password: admin123)
```

### Step 6: Start the Backend Server

```bash
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
Starting up application...
Database initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 7: Test the API

1. Open your browser to: http://localhost:8000/docs
2. You'll see the Swagger UI with all API endpoints
3. Try these endpoints:

**Register a new user:**
- Click on `POST /api/auth/register`
- Click "Try it out"
- Enter:
  ```json
  {
    "email": "you@example.com",
    "username": "yourname",
    "full_name": "Your Full Name",
    "password": "secure_password_123"
  }
  ```
- Click "Execute"

**Login:**
- Click on `POST /api/auth/login`
- Click "Try it out"
- Enter:
  ```json
  {
    "username": "yourname",
    "password": "secure_password_123"
  }
  ```
- Click "Execute"
- Copy the `access_token` from the response

**Authorize:**
- Click the green "Authorize" button at the top
- Enter: `Bearer YOUR_TOKEN_HERE`
- Click "Authorize"

**Get your user info:**
- Click on `GET /api/auth/me`
- Click "Try it out"
- Click "Execute"
- You should see your user data!

## ⚠️ Troubleshooting

### "Cannot connect to database"
- Verify PostgreSQL is running: Open Services (services.msc) and check "postgresql-x64-15" is running
- Check your password in `.env` matches what you set
- Try connecting with psql: `psql -U tableau_user -d tableau_app`

### "Redis connection refused"
- Verify Memurai is running: Open Services and check "Memurai" is running
- Try: `memurai-cli ping` in Command Prompt

### "Module not found" errors
- Make sure virtual environment is activated: `venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

### Port 8000 already in use
- Change PORT in `.env` to something else (e.g., 8001)
- Restart the backend

## 📦 What's Next (Phase 2)

Once the backend is running successfully, we'll build:

1. **Frontend (React + TypeScript)**
   - Login/Registration UI
   - Dashboard layout
   - API integration

2. **Desktop Wrapper (PyWebView)**
   - Embed the web server
   - Create desktop application

3. **Data Connectors**
   - CSV/Excel upload
   - PostgreSQL connection
   - MySQL connection

Would you like me to continue with the frontend or help you get the backend running first?

## 🆘 Get Help

If you encounter issues:
1. Check the error message carefully
2. Verify all prerequisites are installed
3. Check that PostgreSQL and Redis are running
4. Review the `.env` file configuration
5. Try restarting the backend server

Common commands:
```bash
# Check if PostgreSQL is accepting connections
pg_isready -h localhost -p 5432

# Check if Memurai/Redis is running
memurai-cli ping

# View backend logs (run server without uvicorn, with Python directly)
python -m app.main
```
