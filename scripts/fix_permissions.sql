-- Fix permissions for tableau_user
-- Run this as postgres superuser

\c tableau_app

-- Grant all privileges on the public schema
GRANT ALL ON SCHEMA public TO tableau_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tableau_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tableau_user;

-- Grant future privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tableau_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO tableau_user;

-- Make tableau_user the owner of the database
ALTER DATABASE tableau_app OWNER TO tableau_user;

\echo 'Permissions granted successfully!'
