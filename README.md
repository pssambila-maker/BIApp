# Tableau App - Enterprise Business Intelligence Platform

A self-service BI platform built with Python (FastAPI) and React, featuring data connections, transformations, semantic modeling, and interactive dashboards.

## Features

- **Data Collection**: Connect to CSV, Excel, PostgreSQL, MySQL
- **Data Transformation**: Visual pipeline for data prep
- **Semantic Layer**: Define relationships, measures, and dimensions
- **Query Builder**: Drag-and-drop interface for building queries with filters
- **Interactive Dashboards**: Create multi-widget dashboards with charts and visualizations
- **Chart Visualizations**: 10+ chart types (bar, line, pie, scatter, etc.) with sorting and conditional colors
- **Data Export**: Export to Excel, CSV, JSON formats
- **Scheduled Reports & Alerts**: Automated report delivery and data monitoring (In Development)

## Tech Stack

### Backend
- FastAPI + Uvicorn (async Python web framework)
- PostgreSQL (metadata storage)
- DuckDB (analytical query engine)
- Redis (caching and sessions)
- Celery + Redis (background tasks and scheduling)
- SQLAlchemy 2.0 (async ORM)
- Alembic (database migrations)
- Pandas + OpenPyXL (data processing and Excel export)

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

## What You Can Do Right Now

This is a fully functional Business Intelligence platform. Here's what you can do today:

### 1. 📊 **Build Interactive Dashboards**
- Create multi-widget dashboards with drag-and-drop layout
- Add charts, tables, and visualizations to your dashboards
- Configure global filters that affect all widgets
- Save and share dashboards with other users

**Try it**: [Dashboard Builder](http://localhost:3000/dashboards)

### 2. 🔍 **Query Your Data**
- Use the visual Query Builder to explore data without SQL
- Drag dimensions and measures to build queries
- Apply filters with operators (equals, contains, greater than, etc.)
- View results in real-time with automatic chart generation
- Export results to Excel, CSV, or JSON

**Try it**: [Query Builder](http://localhost:3000/query-builder)

### 3. 📈 **Create Visualizations**
Available chart types:
- Bar Chart (vertical/horizontal, grouped/stacked)
- Line Chart (single/multi-series with area fill)
- Pie Chart / Donut Chart
- Scatter Plot with regression lines
- Area Chart (stacked/overlapping)
- Heatmap with color gradients
- Gauge Chart for KPIs
- Funnel Chart for conversion tracking

**Features**:
- Sort by any dimension or measure (ascending/descending)
- Apply conditional colors based on value thresholds
- Interactive tooltips and legends
- Export charts as PNG or PDF

**Try it**: Create a query, then switch between chart types

### 4. 📚 **Build Semantic Models**
- Define semantic entities from your data sources
- Create reusable dimensions and measures
- Configure aggregations (SUM, AVG, COUNT, MIN, MAX)
- Add calculated fields with SQL expressions
- Browse the semantic catalog to discover available data

**Try it**: [Semantic Catalog](http://localhost:3000/catalog)

### 5. 🔌 **Connect Data Sources**
Supported connectors:
- **CSV Files**: Upload local CSV files
- **Excel Files**: Upload .xlsx files
- **PostgreSQL**: Connect to Postgres databases
- **MySQL**: Connect to MySQL databases

**Try it**: [Data Sources](http://localhost:3000/data-sources)

### 6. 🔄 **Transform Data**
- Create visual transformation pipelines
- Apply filters, joins, aggregations
- Preview transformations in real-time
- Save and reuse transformation workflows

### 7. 📤 **Export and Share**
- Export query results to Excel, CSV, JSON
- Export charts as PNG images
- Save queries for reuse
- Share dashboards with team members

### 8. 👥 **User Management** (Admin)
- Create and manage user accounts
- Assign roles and permissions (Admin, Analyst, Viewer)
- Track user sessions and activity
- Secure data access with row-level security

**Admin Access**: [http://localhost:8000/docs](http://localhost:8000/docs) → Use `/api/users` endpoints

### 9. 🔍 **Sample Data Available**
The app comes with the **Superstore dataset** (9,994 rows) pre-loaded:
- Order data with customer, product, sales metrics
- Multiple semantic entities configured
- Ready to explore with Query Builder
- Perfect for testing dashboards and charts

## Quick Access Links

### Application URLs
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Dashboards**: [http://localhost:3000/dashboards](http://localhost:3000/dashboards)
- **Query Builder**: [http://localhost:3000/query-builder](http://localhost:3000/query-builder)
- **Semantic Catalog**: [http://localhost:3000/catalog](http://localhost:3000/catalog)
- **Data Sources**: [http://localhost:3000/data-sources](http://localhost:3000/data-sources)

## Documentation

Comprehensive guides for common operations:

- **[PostgreSQL Operations Guide](POSTGRESQL_OPERATIONS.md)** - Database setup, user management, password reset, loading CSV data
- **[Semantic Catalog Guide](SEMANTIC_CATALOG_GUIDE.md)** - Creating entities, dimensions, measures, and using the Query Builder
- **[Chart Sorting and Colors Guide](CHART_SORTING_AND_COLORS_GUIDE.md)** - Sorting charts and applying conditional colors like Tableau Desktop
- **[Admin User Management](ADMIN_USER_MANAGEMENT.md)** - User administration and permissions
- **[Chart Visualization Testing](CHART_VISUALIZATION_TESTING.md)** - Testing chart features
- **[Phase 4 Testing Guide](PHASE4_TESTING_GUIDE.md)** - Comprehensive testing procedures
- **[Quick Admin Guide](QUICK_ADMIN_GUIDE.md)** - Quick reference for administrators

## Current Status

✅ **Completed Phases**:
- Phase 1: Enterprise BI Platform Backend (Auth, RBAC, Data Sources)
- Phase 2: Data Collection Layer (CSV, Excel, PostgreSQL connectors)
- Phase 3: Data Transformation Engine (Visual pipeline system)
- Phase 4: Semantic Layer (Entities, Dimensions, Measures)
- Phase 5 & 6: Frontend with Query Builder
- Phase 7: Dashboard Builder (Multi-widget dashboards with drag-and-drop)
- Phase 8: Data Visualization (10+ chart types, sorting, conditional colors, export)

🚧 **In Progress** (Week 2 of 8 Completed):
- Phase 9: Scheduled Reports & Alerts
  - ✅ Week 1: Database models (ScheduledReport, Alert, EmailConfiguration, ReportExecution, AlertExecution)
  - ✅ Week 1: Celery + Redis task queue configured and tested
  - ✅ Week 2: Services layer (ScheduleService, ReportService, EmailService, EncryptionService)
  - ✅ Week 2: Report generation (Excel, CSV, PDF with styling)
  - ✅ Week 2: Email delivery with SMTP and encryption
  - 🔄 Week 3: API endpoints and Pydantic schemas (Next)
  - 📋 Week 4-8: Celery task implementation and frontend UI

## Sample Data

The project includes sample data loaded in PostgreSQL:

1. **Superstore Dataset** (9,994 rows)
   - Table: `superstore`
   - Contains: Orders, customers, products, sales metrics
   - Columns: order_id, customer_name, product_name, sales, profit, quantity, discount, etc.

2. **Sales Data Q1 2024** (CSV)
   - Sample sales transactions
   - Used for Customer and Product entities

## Support

For issues and questions, please open an issue on GitHub.
