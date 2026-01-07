# Complete Testing Guide - BI Platform

This guide walks you through testing all features implemented so far (Phase 1 + Phase 2).

## Prerequisites

✅ Backend server running on http://localhost:8000
✅ PostgreSQL database running
✅ Sample data files created in `backend/sample_data/`

---

## Part 1: Authentication System (Phase 1)

### Step 1: Access Swagger UI

1. Open your web browser
2. Navigate to: **http://localhost:8000/docs**
3. You should see the FastAPI Swagger documentation interface

### Step 2: Register a New User

1. Find the **POST /api/register** endpoint
2. Click "Try it out"
3. Enter the following JSON:
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "Test@1234",
     "full_name": "Test User"
   }
   ```
4. Click "Execute"
5. **Expected Result**: Status 200, response shows user details with `id` and `created_at`

### Step 3: Login

1. Find the **POST /api/login** endpoint
2. Click "Try it out"
3. Enter:
   ```json
   {
     "username": "testuser",
     "password": "Test@1234"
   }
   ```
4. Click "Execute"
5. **Expected Result**: Status 200, response contains `access_token`
6. **IMPORTANT**: Copy the `access_token` value (you'll need it for authenticated requests)

### Step 4: Authenticate in Swagger

1. Scroll to the top of the Swagger page
2. Click the **"Authorize"** button (lock icon)
3. In the dialog, enter: `Bearer YOUR_ACCESS_TOKEN_HERE`
   - Replace `YOUR_ACCESS_TOKEN_HERE` with the token from Step 3
   - Make sure to include the word "Bearer" followed by a space
4. Click "Authorize"
5. Click "Close"

### Step 5: Get Current User Profile

1. Find the **GET /api/me** endpoint
2. Click "Try it out"
3. Click "Execute"
4. **Expected Result**: Status 200, shows your user profile details

### Step 6: Test Logout

1. Find the **POST /api/logout** endpoint
2. Click "Try it out"
3. Click "Execute"
4. **Expected Result**: Status 204 (No Content)

---

## Part 2: Data Source Management (Phase 2)

### Step 7: Re-login (if you logged out)

Repeat Step 3 and Step 4 to get a fresh token and authorize again.

### Step 8: Create a CSV Data Source

1. Find the **POST /api/data-sources** endpoint
2. Click "Try it out"
3. Enter the following JSON (adjust path if needed):
   ```json
   {
     "name": "Sales Data Q1 2024",
     "type": "csv",
     "description": "Sample sales data for testing",
     "connection_config": {
       "file_path": "C:\\Users\\sambi\\OneDrive\\TableauApp\\backend\\sample_data\\sales_data.csv",
       "delimiter": ",",
       "has_header": true,
       "encoding": "utf-8"
     }
   }
   ```
4. Click "Execute"
5. **Expected Result**: Status 201, response shows data source with an `id`
6. **IMPORTANT**: Copy the data source `id` (you'll need it for next steps)

### Step 9: Test CSV Connection

1. Find the **POST /api/data-sources/{data_source_id}/test** endpoint
2. Click "Try it out"
3. Enter the data source `id` from Step 8
4. Click "Execute"
5. **Expected Result**: Status 200
   ```json
   {
     "status": "success",
     "message": "Successfully connected to CSV file"
   }
   ```

### Step 10: List Tables from CSV

1. Find the **GET /api/data-sources/{data_source_id}/tables** endpoint
2. Click "Try it out"
3. Enter the data source `id` from Step 8
4. Set `refresh` to `true`
5. Click "Execute"
6. **Expected Result**: Status 200, shows table information
   ```json
   [
     {
       "table_name": "sales_data",
       "schema_name": null,
       "row_count": 20,
       "size_bytes": ...
     }
   ]
   ```

### Step 11: Get CSV Table Schema

1. Find the **GET /api/data-sources/{data_source_id}/tables/{table_name}/schema** endpoint
2. Click "Try it out"
3. Enter:
   - `data_source_id`: your CSV data source id
   - `table_name`: `sales_data`
4. Click "Execute"
5. **Expected Result**: Status 200, shows column information
   ```json
   {
     "table_name": "sales_data",
     "columns": [
       {"name": "order_id", "type": "integer", "nullable": true},
       {"name": "customer_name", "type": "string", "nullable": true},
       {"name": "product", "type": "string", "nullable": true},
       {"name": "quantity", "type": "integer", "nullable": true},
       {"name": "unit_price", "type": "float", "nullable": true},
       {"name": "order_date", "type": "date", "nullable": true},
       {"name": "region", "type": "string", "nullable": true}
     ],
     "row_count": 20
   }
   ```

### Step 12: Preview CSV Data

1. Find the **GET /api/data-sources/{data_source_id}/tables/{table_name}/preview** endpoint
2. Click "Try it out"
3. Enter:
   - `data_source_id`: your CSV data source id
   - `table_name`: `sales_data`
   - `limit`: `10`
4. Click "Execute"
5. **Expected Result**: Status 200, shows first 10 rows of data
   ```json
   {
     "columns": ["order_id", "customer_name", "product", ...],
     "data": [
       {
         "order_id": 1001,
         "customer_name": "John Smith",
         "product": "Laptop",
         "quantity": 2,
         "unit_price": 1200.0,
         "order_date": "2024-01-15",
         "region": "North"
       },
       ...
     ],
     "row_count": 10
   }
   ```

### Step 13: Create an Excel Data Source

1. Find the **POST /api/data-sources** endpoint again
2. Click "Try it out"
3. Enter the following JSON:
   ```json
   {
     "name": "Employee and Project Data",
     "type": "excel",
     "description": "HR and project management data",
     "connection_config": {
       "file_path": "C:\\Users\\sambi\\OneDrive\\TableauApp\\backend\\sample_data\\employees_projects.xlsx"
     }
   }
   ```
4. Click "Execute"
5. **Expected Result**: Status 201, response shows data source with an `id`
6. **IMPORTANT**: Copy this Excel data source `id`

### Step 14: List Sheets from Excel File

1. Find the **GET /api/data-sources/{data_source_id}/tables** endpoint
2. Click "Try it out"
3. Enter the Excel data source `id` from Step 13
4. Set `refresh` to `true`
5. Click "Execute"
6. **Expected Result**: Status 200, shows both sheets
   ```json
   [
     {
       "table_name": "Employees",
       "row_count": 30,
       ...
     },
     {
       "table_name": "Projects",
       "row_count": 15,
       ...
     }
   ]
   ```

### Step 15: Preview Excel Sheet Data

1. Find the **GET /api/data-sources/{data_source_id}/tables/{table_name}/preview** endpoint
2. Click "Try it out"
3. Enter:
   - `data_source_id`: your Excel data source id
   - `table_name`: `Employees`
   - `limit`: `5`
4. Click "Execute"
5. **Expected Result**: Status 200, shows first 5 employee records

### Step 16: List All Your Data Sources

1. Find the **GET /api/data-sources** endpoint
2. Click "Try it out"
3. Click "Execute"
4. **Expected Result**: Status 200, shows both data sources you created (CSV and Excel)

### Step 17: Update a Data Source

1. Find the **PUT /api/data-sources/{data_source_id}** endpoint
2. Click "Try it out"
3. Enter your CSV data source `id`
4. Enter update data:
   ```json
   {
     "description": "Updated description - Q1 2024 sales figures",
     "is_certified": true
   }
   ```
5. Click "Execute"
6. **Expected Result**: Status 200, shows updated data source with new description and `is_certified: true`

### Step 18: Test PostgreSQL Connection (Optional)

If you want to test connecting to your PostgreSQL database as a data source:

1. Find the **POST /api/data-sources** endpoint
2. Enter:
   ```json
   {
     "name": "Local PostgreSQL - Tableau DB",
     "type": "postgresql",
     "description": "Connection to local PostgreSQL database",
     "connection_config": {
       "host": "localhost",
       "port": 5432,
       "database": "tableau_app",
       "username": "postgres",
       "password": "postgres123",
       "schema": "public"
     }
   }
   ```
3. Click "Execute"
4. Copy the data source `id`
5. Test the connection using **POST /api/data-sources/{id}/test**
6. List tables using **GET /api/data-sources/{id}/tables**
7. **Expected Result**: You should see the tables `users`, `roles`, `user_roles`, `user_sessions`, `data_sources`, `data_source_tables`

### Step 19: Delete a Data Source (Optional)

1. Find the **DELETE /api/data-sources/{data_source_id}** endpoint
2. Click "Try it out"
3. Enter a data source `id` you want to delete
4. Click "Execute"
5. **Expected Result**: Status 204 (No Content)
6. Verify deletion by listing all data sources (Step 16)

---

## Part 3: Verify in Database (Optional)

If you want to verify the data is actually stored in PostgreSQL:

1. Open a terminal
2. Connect to PostgreSQL:
   ```bash
   psql -U postgres -d tableau_app
   ```
3. Run queries:
   ```sql
   -- View all users
   SELECT id, username, email, created_at FROM users;

   -- View all data sources
   SELECT id, name, type, description, is_certified, created_at FROM data_sources;

   -- View user sessions
   SELECT user_id, expires_at, created_at FROM user_sessions;
   ```

---

## Expected Results Summary

After completing all steps, you should have:

✅ **1 User Account** - created and authenticated
✅ **2+ Data Sources** - CSV and Excel (optionally PostgreSQL)
✅ **Tested Connections** - verified all data sources connect successfully
✅ **Schema Discovery** - viewed column information for tables/sheets
✅ **Data Preview** - previewed actual data from CSV and Excel files
✅ **CRUD Operations** - created, read, updated data sources

---

## Troubleshooting

### Issue: "Unauthorized" error
**Solution**: Make sure you clicked "Authorize" and entered `Bearer YOUR_TOKEN` with the token from login.

### Issue: File not found error
**Solution**: Verify the file paths in the connection_config match your actual file locations.

### Issue: Connection test fails
**Solution**:
- For CSV/Excel: Check file path and file exists
- For PostgreSQL: Verify credentials and database is running

### Issue: Server not responding
**Solution**:
- Check if backend server is running: http://localhost:8000/health
- Restart server if needed

---

## Next Steps

Once all tests pass, you're ready for:
- **Phase 3**: Data Transformation Engine (visual data pipeline builder)
- **Phase 4**: Semantic Layer (business metrics and calculations)
- **Phase 5**: Analytics Canvas (drag-and-drop visualization builder)
