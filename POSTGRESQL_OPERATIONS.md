# PostgreSQL Operations Guide

This guide covers common PostgreSQL operations for the BI Platform.

## Quick Access Links

- **BI Platform**: [http://localhost:3000](http://localhost:3000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Semantic Catalog**: [http://localhost:3000/catalog](http://localhost:3000/catalog)
- **Query Builder**: [http://localhost:3000/query-builder](http://localhost:3000/query-builder)

## Table of Contents
- [Connection Information](#connection-information)
- [Reset Superuser Password](#reset-superuser-password)
- [Database Management](#database-management)
- [User Management](#user-management)
- [Schema and Table Operations](#schema-and-table-operations)
- [Loading CSV Data](#loading-csv-data)
- [Troubleshooting](#troubleshooting)

---

## Connection Information

### Current Setup
- **Host**: localhost
- **Port**: 5432
- **Database**: tableau_app
- **Superuser**: postgres
- **Password**: Test@1234
- **Application User**: tableau_user
- **Application Password**: MySecurePassword123

### Connection String
```
postgresql://postgres:Test@1234@localhost:5432/tableau_app
```

For Python/asyncpg (URL-encoded):
```
postgresql+asyncpg://postgres:Test%401234@localhost/tableau_app
```

---

## Reset Superuser Password

If you forget the postgres superuser password, follow these steps:

### Step 1: Open Administrator Command Prompt
- Press Windows key
- Type "cmd"
- Right-click "Command Prompt"
- Select "Run as administrator"

### Step 2: Stop PostgreSQL Service
```bash
net stop postgresql-x64-16
```

### Step 3: Backup pg_hba.conf
```bash
copy "C:\Program Files\PostgreSQL\16\data\pg_hba.conf" "C:\Program Files\PostgreSQL\16\data\pg_hba.conf.backup"
```

### Step 4: Edit pg_hba.conf
```bash
notepad "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
```

Change all authentication methods to `trust`:
```
# Before
host    all             all             127.0.0.1/32            scram-sha-256

# After
host    all             all             127.0.0.1/32            trust
```

Do this for all lines (local, host IPv4, host IPv6, replication).

### Step 5: Start PostgreSQL Service
```bash
net start postgresql-x64-16
```

### Step 6: Connect and Reset Password
```bash
psql -U postgres -d postgres
```

In the PostgreSQL prompt:
```sql
ALTER USER postgres WITH PASSWORD 'YourNewPassword';
\q
```

### Step 7: Restore Original pg_hba.conf
```bash
copy "C:\Program Files\PostgreSQL\16\data\pg_hba.conf.backup" "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
```

### Step 8: Restart PostgreSQL
```bash
net stop postgresql-x64-16
net start postgresql-x64-16
```

### Step 9: Update Backend Configuration
Edit `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YourNewPassword@localhost/tableau_app
```

**Note**: URL-encode special characters:
- `@` → `%40`
- `#` → `%23`
- `&` → `%26`
- `:` → `%3A`

Example: `Test@1234` → `Test%401234`

---

## Database Management

### List All Databases
```bash
psql -U postgres -d postgres -c "\l"
```

Or in psql:
```sql
\l
```

### Create a New Database
```sql
CREATE DATABASE mydb;
```

### Drop a Database
```sql
DROP DATABASE mydb;
```

### Connect to a Database
```bash
psql -U postgres -d tableau_app
```

Or in psql:
```sql
\c tableau_app
```

### Database Size
```sql
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;
```

---

## User Management

### List All Users
```sql
\du
```

Or:
```sql
SELECT usename, usesuper, usecreatedb FROM pg_user;
```

### Create a New User
```sql
CREATE USER myuser WITH PASSWORD 'mypassword';
```

### Grant Privileges
```sql
-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE tableau_app TO myuser;

-- Grant all privileges on all tables in schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;

-- Grant create permission on schema
GRANT CREATE ON SCHEMA public TO myuser;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO myuser;
```

### Change User Password
```sql
ALTER USER myuser WITH PASSWORD 'newpassword';
```

### Drop a User
```sql
DROP USER myuser;
```

---

## Schema and Table Operations

### List All Tables
```sql
\dt
```

Or:
```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

### Show Table Structure
```sql
\d tablename
```

Or:
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tablename'
ORDER BY ordinal_position;
```

### Create a Table
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10,2),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### View Table Data
```sql
-- First 10 rows
SELECT * FROM products LIMIT 10;

-- Count rows
SELECT COUNT(*) FROM products;

-- Table size
SELECT pg_size_pretty(pg_total_relation_size('products'));
```

### Drop a Table
```sql
DROP TABLE products;
```

---

## Loading CSV Data

### Method 1: Using Python (Recommended)

```python
import pandas as pd
import psycopg2

# Read CSV
df = pd.read_csv('path/to/data.csv', encoding='latin-1')

# Connect to database
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='tableau_app',
    user='postgres',
    password='Test@1234'
)
conn.autocommit = True
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE mytable (
        id INTEGER PRIMARY KEY,
        name VARCHAR(255),
        value NUMERIC(10,2)
    );
''')

# Insert data
for idx, row in df.iterrows():
    cursor.execute('''
        INSERT INTO mytable (id, name, value)
        VALUES (%s, %s, %s)
    ''', (row['id'], row['name'], row['value']))

    if idx % 1000 == 0:
        print(f'Inserted {idx} rows...')

cursor.close()
conn.close()
```

### Method 2: Using PostgreSQL COPY Command

```sql
COPY mytable FROM 'C:/path/to/data.csv'
DELIMITER ','
CSV HEADER;
```

**Note**: The file path must be accessible by the PostgreSQL server process.

---

## Troubleshooting

### Connection Issues

**Error**: `password authentication failed`
- Check username and password
- Verify pg_hba.conf authentication method
- Ensure PostgreSQL service is running

**Error**: `database does not exist`
- Create the database first: `CREATE DATABASE tableau_app;`
- Verify database name spelling

### Permission Issues

**Error**: `permission denied for schema public`
```sql
GRANT ALL PRIVILEGES ON SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
```

**Error**: `permission denied for table`
```sql
GRANT ALL PRIVILEGES ON TABLE mytable TO myuser;
```

### Service Issues

**Check if PostgreSQL is running**:
```bash
sc query postgresql-x64-16
```

**Start service**:
```bash
net start postgresql-x64-16
```

**Stop service**:
```bash
net stop postgresql-x64-16
```

### Common Commands

```bash
# Check PostgreSQL version
psql -U postgres -c "SELECT version();"

# Check active connections
psql -U postgres -d postgres -c "SELECT * FROM pg_stat_activity;"

# Kill a connection
psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = 12345;"

# Reload configuration
psql -U postgres -c "SELECT pg_reload_conf();"
```

---

## Quick Reference

### Connect to Database
```bash
psql -U postgres -d tableau_app
```

### Common psql Commands
```
\l              - List databases
\c dbname       - Connect to database
\dt             - List tables
\d tablename    - Describe table
\du             - List users
\q              - Quit
\?              - Help
```

### Export Data
```bash
# Export to CSV
psql -U postgres -d tableau_app -c "COPY (SELECT * FROM mytable) TO STDOUT WITH CSV HEADER" > output.csv

# Export entire database
pg_dump -U postgres tableau_app > backup.sql
```

### Import Data
```bash
# Import SQL dump
psql -U postgres -d tableau_app < backup.sql
```
