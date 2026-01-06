# Quick Setup Checklist

## Phase 1: Install Prerequisites ⏱️ ~30 minutes

### ✅ Already Installed
- [x] Python 3.11.9
- [x] Node.js 22.16.0
- [x] Git 2.50.1

### 📥 To Install Now

- [ ] **PostgreSQL 16** (~15 minutes)
  - Download: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
  - Password to set: `__________` (write it down!)
  - Verify: `psql --version`

- [ ] **Memurai (Redis)** (~10 minutes)
  - Download: https://www.memurai.com/get-memurai
  - Start service after install
  - Verify: `memurai-cli ping` (should return PONG)

- [ ] **Create Database** (~2 minutes)
  ```sql
  psql -U postgres
  CREATE DATABASE tableau_app;
  CREATE USER tableau_user WITH PASSWORD 'MySecurePassword123';
  \c tableau_app
  GRANT ALL ON SCHEMA public TO tableau_user;
  \q
  ```

## Phase 2: Backend Setup ⏱️ ~10 minutes

- [ ] **Create Virtual Environment**
  ```bash
  cd c:\Users\sambi\OneDrive\TableauApp\backend
  python -m venv venv
  venv\Scripts\activate
  ```

- [ ] **Install Dependencies** (~5 minutes)
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Configure Environment**
  ```bash
  copy .env.example .env
  notepad .env
  ```
  Update these lines:
  - `DATABASE_URL=postgresql+asyncpg://tableau_user:MySecurePassword123@localhost/tableau_app`
  - `SECRET_KEY=` (generate random 32+ characters)

- [ ] **Initialize Database**
  ```bash
  python ..\scripts\init_db.py
  ```
  Should see: ✓ Database tables created

## Phase 3: Test Backend ⏱️ ~5 minutes

- [ ] **Start Server**
  ```bash
  python -m app.main
  ```
  Should see: Uvicorn running on http://127.0.0.1:8000

- [ ] **Test API** (in browser)
  - Open: http://localhost:8000/docs
  - Try: POST /api/auth/register
  - Try: POST /api/auth/login
  - Copy token and click "Authorize"
  - Try: GET /api/auth/me

## Quick Commands Reference

```bash
# Start PostgreSQL service
net start postgresql-x64-16

# Start Memurai service
net start Memurai

# Activate Python virtual environment
cd c:\Users\sambi\OneDrive\TableauApp\backend
venv\Scripts\activate

# Start backend server
python -m app.main

# Or use the batch script:
..\scripts\start_backend.bat
```

## Verification Commands

```bash
# Check if PostgreSQL is running
sc query postgresql-x64-16

# Check if Memurai is running
sc query Memurai

# Test PostgreSQL connection
psql -U tableau_user -d tableau_app

# Test Redis connection
memurai-cli ping

# Check Python virtual environment
where python
# Should show: C:\Users\sambi\OneDrive\TableauApp\backend\venv\Scripts\python.exe
```

## Next Steps After Backend is Running

1. **Build Frontend** (React + TypeScript)
2. **Create Desktop App** (PyWebView)
3. **Add Data Connectors** (CSV, PostgreSQL, MySQL)
4. **Build Transformation Engine**
5. **Implement Semantic Layer**

---

## Current Step: Install PostgreSQL and Redis

📖 See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed instructions.

Once installed, let me know and I'll help with the backend setup!
