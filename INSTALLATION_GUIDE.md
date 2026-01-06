# Installation Guide - PostgreSQL and Redis Setup

## Current Status ✅

- ✅ Python 3.11.9 installed
- ✅ Node.js 22.16.0 installed
- ✅ Git 2.50.1 installed
- ❌ PostgreSQL not installed
- ❌ Redis not installed

## Step 1: Install PostgreSQL

### Download PostgreSQL

1. Go to: https://www.postgresql.org/download/windows/
2. Click "Download the installer"
3. Download **PostgreSQL 16.x** for Windows x86-64
4. Direct link: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

### Install PostgreSQL

1. **Run the installer** (postgresql-16.x-windows-x64.exe)

2. **Installation wizard steps:**
   - Click "Next"
   - Installation Directory: Keep default (`C:\Program Files\PostgreSQL\16`)
   - Select Components: Check all (PostgreSQL Server, pgAdmin 4, Stack Builder, Command Line Tools)
   - Data Directory: Keep default
   - **Password**: Enter a password you'll remember (e.g., `postgres123`)
     - ⚠️ **IMPORTANT**: Write this password down! You'll need it later.
   - Port: Keep default `5432`
   - Locale: Default locale
   - Click "Next" and "Install"
   - Wait for installation (3-5 minutes)
   - Uncheck "Launch Stack Builder" at the end
   - Click "Finish"

3. **Verify installation:**
   - Open a **NEW** Command Prompt (important - to pick up new PATH)
   - Run: `psql --version`
   - You should see: `psql (PostgreSQL) 16.x`

### Create Database and User

1. **Open Command Prompt as Administrator**

2. **Connect to PostgreSQL:**
   ```bash
   psql -U postgres
   ```
   - Enter the password you set during installation

3. **Run these SQL commands:**
   ```sql
   CREATE DATABASE tableau_app;
   CREATE USER tableau_user WITH PASSWORD 'MySecurePassword123';
   GRANT ALL PRIVILEGES ON DATABASE tableau_app TO tableau_user;

   -- Grant schema privileges (PostgreSQL 15+)
   \c tableau_app
   GRANT ALL ON SCHEMA public TO tableau_user;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tableau_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tableau_user;

   -- Exit
   \q
   ```

4. **Test the connection:**
   ```bash
   psql -U tableau_user -d tableau_app
   ```
   - Enter password: `MySecurePassword123`
   - If you see `tableau_app=>`, it worked! Type `\q` to exit.

## Step 2: Install Redis (Memurai)

Redis doesn't have official Windows support, so we'll use **Memurai** (Redis-compatible).

### Download Memurai

1. Go to: https://www.memurai.com/get-memurai
2. Click "Download Memurai Developer"
3. Fill in the form (or use a temporary email)
4. Download **Memurai Developer** (free version)

### Install Memurai

1. **Run the installer** (Memurai-Developer-vX.X.X.msi)

2. **Installation wizard steps:**
   - Accept the license agreement
   - Installation folder: Keep default
   - Click "Install"
   - Click "Finish"

3. **Start Memurai service:**
   - Open Services (press Win + R, type `services.msc`, press Enter)
   - Find "Memurai" in the list
   - Right-click → Start
   - Right-click → Properties → Startup type → Automatic (so it starts with Windows)

4. **Verify installation:**
   - Open Command Prompt
   - Run: `memurai-cli ping`
   - You should see: `PONG`

### Alternative: Docker (Optional)

If you prefer Docker for PostgreSQL and Redis:

```bash
# Install Docker Desktop for Windows first
# Then run:

docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16
docker run -d --name redis -p 6379:6379 redis:7
```

## Step 3: Verify Everything is Running

### Check PostgreSQL
```bash
# Check if service is running
sc query postgresql-x64-16

# Test connection
psql -U tableau_user -d tableau_app
# Enter password: MySecurePassword123
# Type \q to exit
```

### Check Redis/Memurai
```bash
# Test connection
memurai-cli ping
# Should return: PONG

# Check if service is running
sc query Memurai
```

## Troubleshooting

### PostgreSQL Issues

**"psql: command not found"**
- Restart Command Prompt after installation
- Or add to PATH manually: `C:\Program Files\PostgreSQL\16\bin`

**"password authentication failed"**
- Make sure you're using the correct password
- Try resetting: `psql -U postgres` then `ALTER USER tableau_user WITH PASSWORD 'NewPassword';`

**"could not connect to server"**
- Check if service is running: Open Services, look for "postgresql-x64-16"
- Start it if stopped

### Redis/Memurai Issues

**"Could not connect to Redis"**
- Check if Memurai service is running (Services → Memurai → Start)
- Try restarting the service

**"memurai-cli: command not found"**
- Add to PATH: `C:\Program Files\Memurai\`
- Or use full path: `"C:\Program Files\Memurai\memurai-cli.exe" ping`

### Windows Firewall

If you have connection issues:
- Open Windows Firewall
- Allow PostgreSQL (port 5432)
- Allow Memurai (port 6379)

## Ready for Next Step?

Once both PostgreSQL and Redis are installed and running, you can proceed to:

1. Set up the Python virtual environment
2. Install dependencies
3. Configure the `.env` file
4. Initialize the database
5. Start the backend server

Run this command to continue:
```bash
cd c:\Users\sambi\OneDrive\TableauApp\backend
```

Let me know when PostgreSQL and Redis are installed, and I'll help with the next steps!
