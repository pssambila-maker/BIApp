-- Create database and user for Tableau App
-- Run this script as the postgres superuser

-- Create the database
CREATE DATABASE tableau_app;

-- Create the user with password
CREATE USER tableau_user WITH PASSWORD 'TableauApp2024!';

-- Connect to the new database
\c tableau_app

-- Grant privileges on the database
GRANT ALL PRIVILEGES ON DATABASE tableau_app TO tableau_user;

-- Grant privileges on schema (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO tableau_user;

-- Grant privileges on future tables and sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tableau_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO tableau_user;

-- Display success message
\echo 'Database tableau_app and user tableau_user created successfully!'
\echo 'You can now connect with: psql -U tableau_user -d tableau_app'
