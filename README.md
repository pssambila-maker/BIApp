# Tableau App - Enterprise Business Intelligence Platform

A self-service BI platform built with Python (FastAPI) and React, featuring data connections, transformations, semantic modeling, and interactive dashboards.

## Features

- **Data Collection**: Connect to CSV, Excel, PostgreSQL, MySQL
- **Data Transformation**: Visual pipeline for data prep
- **Semantic Layer**: Define relationships, measures, and dimensions
- **Interactive Analytics**: Drag-and-drop canvas with real-time visualizations
- **Publishing & Sharing**: RBAC, exports (PDF, PNG, CSV), shareable dashboards

## Tech Stack

### Backend
- FastAPI + Uvicorn (async Python web framework)
- PostgreSQL (metadata storage)
- DuckDB (analytical query engine)
- Redis (caching and sessions)
- SQLAlchemy 2.0 (async ORM)
- Alembic (database migrations)

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Ant Design (UI components)
- Apache ECharts (charting)
- React Query (data fetching)
- Zustand (state management)

### Desktop
- PyWebView (lightweight desktop wrapper)

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+**
   ```bash
   python --version
   ```

2. **Node.js 18+ and npm**
   ```bash
   node --version && npm --version
   ```

3. **PostgreSQL 15+**
   - Download from: https://www.postgresql.org/download/
   - Create database and user (see setup below)

4. **Redis 7+**
   - Windows: Use Memurai (https://www.memurai.com/) or WSL2
   - Verify: `redis-cli ping` (should return PONG)

5. **Git**
   ```bash
   git --version
   ```

## Quick Start

### 1. Clone and Setup

```bash
cd c:\Users\sambi\OneDrive\TableauApp

# Initialize git
git init
git add .
git commit -m "Initial commit"
```

### 2. Database Setup

```bash
# Open PostgreSQL command line (psql)
psql -U postgres

# Create database and user
CREATE DATABASE tableau_app;
CREATE USER tableau_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE tableau_app TO tableau_user;
\q
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env and update:
# - DATABASE_URL with your password
# - SECRET_KEY (generate a secure random string)
# - ENCRYPTION_KEY (optional, for data source credentials)

# Initialize database
python ..\scripts\init_db.py

# Start the backend server
python -m app.main
```

Backend will be running at: http://localhost:8000

API documentation: http://localhost:8000/docs

### 4. Frontend Setup (Coming Next)

```bash
cd frontend

# Install Vite and create React + TypeScript app
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
npm install @tanstack/react-query zustand axios
npm install ant design echarts-for-react ag-grid-react ag-grid-community
npm install @dnd-kit/core @dnd-kit/sortable

# Start development server
npm run dev
```

Frontend will be running at: http://localhost:5173

### 5. Test the Backend API

1. Open http://localhost:8000/docs
2. Try the `/api/auth/register` endpoint to create a user
3. Use `/api/auth/login` to get an access token
4. Click "Authorize" and enter your token
5. Test protected endpoints like `/api/auth/me`

Default admin credentials (after running init_db.py):
- **Username**: admin
- **Password**: admin123 (CHANGE THIS!)

## Project Structure

```
tableau_app/
├── backend/                    # Python backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Business logic
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Service layer
│   │   ├── db/                # Database config
│   │   └── utils/             # Utilities
│   ├── requirements.txt
│   └── .env
├── frontend/                   # React frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── desktop/                    # PyWebView wrapper
├── scripts/                    # Utility scripts
└── docs/                       # Documentation
```

## Development Workflow

### Running Backend (Development)

```bash
cd backend
venv\Scripts\activate  # Windows
python -m app.main
```

### Running Frontend (Development)

```bash
cd frontend
npm run dev
```

### Database Migrations

```bash
cd backend
venv\Scripts\activate

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Running Tests

```bash
cd backend
pytest tests/
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout (invalidate session)
- `GET /api/auth/me` - Get current user info

### Coming Soon
- Data Sources API
- Transformations API
- Semantic Models API
- Dashboards API
- Query Execution API

## Configuration

Key environment variables in `.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT signing key (keep secret!)
- `ENCRYPTION_KEY`: Fernet key for encrypting data source credentials
- `CORS_ORIGINS`: Allowed frontend origins
- `ACCESS_TOKEN_EXPIRE_HOURS`: JWT token expiration (default: 8)

## Security Notes

1. **Change default admin password** immediately after setup
2. **Generate a strong SECRET_KEY** for production
3. **Use HTTPS** in production
4. **Enable ENCRYPTION_KEY** before adding data sources with credentials
5. **Review CORS_ORIGINS** for production deployment

## Troubleshooting

### Cannot connect to PostgreSQL
- Verify PostgreSQL is running: `pg_isready`
- Check connection string in `.env`
- Ensure database and user exist

### Cannot connect to Redis
- Windows: Start Memurai service
- Verify: `redis-cli ping`
- Check `REDIS_URL` in `.env`

### Import errors in Python
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend cannot connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in backend config
- Verify API base URL in frontend

## Next Steps

- [ ] Complete frontend implementation
- [ ] Add data source connectors (CSV, PostgreSQL, MySQL)
- [ ] Build transformation engine
- [ ] Implement semantic layer
- [ ] Create analytics canvas
- [ ] Add dashboard builder
- [ ] Implement PyWebView desktop wrapper

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
