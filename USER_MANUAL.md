# Tableau App - Complete User Manual

**Version**: 1.0
**Last Updated**: January 12, 2026

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Builder](#dashboard-builder)
3. [Query Builder](#query-builder)
4. [Chart Visualizations](#chart-visualizations)
5. [Scheduled Reports & Alerts](#scheduled-reports--alerts)
6. [Semantic Catalog](#semantic-catalog)
7. [Data Sources](#data-sources)
8. [Data Transformations](#data-transformations)
9. [User Management](#user-management)
10. [Data Export](#data-export)
11. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### First Time Login

1. Navigate to [http://localhost:3000](http://localhost:3000)
2. Click **"Login"**
3. Use default credentials:
   - **Email**: `frontend@test.com`
   - **Password**: `password123`
4. **Important**: Change your password after first login

### Navigation

The application has a top navigation bar with these sections:
- **Home**: Dashboard overview
- **Dashboards**: Create and view dashboards
- **Query Builder**: Explore data with visual queries
- **Scheduled Reports**: Automate report delivery (coming soon)
- **Alerts**: Data monitoring (coming soon)
- **Catalog**: Browse semantic models
- **Data Sources**: Manage connections
- **Settings**: Email configuration and preferences

---

## Dashboard Builder

### Creating a Dashboard

1. Click **"Dashboards"** in the navigation menu
2. Click **"New Dashboard"** button
3. Enter dashboard details:
   - **Name**: Give your dashboard a descriptive name
   - **Description**: Optional summary of what the dashboard shows
4. Click **"Create"**

### Adding Widgets

1. Open your dashboard
2. Click **"Add Widget"** button
3. Select widget type:
   - **Chart Widget**: Visualize data with charts
   - **Table Widget**: Display data in tabular format
   - **Text Widget**: Add titles, descriptions, or notes
   - **Filter Widget**: Create global filters
4. Configure the widget:
   - **Title**: Widget heading
   - **Entity**: Select data source (Customer, Order, Product, etc.)
   - **Dimensions**: Fields to group by (e.g., Category, Region)
   - **Measures**: Metrics to display (e.g., Sales, Profit, Quantity)
   - **Chart Type**: Bar, Line, Pie, Scatter, etc.
5. Click **"Add to Dashboard"**

### Arranging Widgets

- **Drag and Drop**: Click and hold widget title bar to move
- **Resize**: Drag widget corners to resize
- **Remove**: Click the trash icon on widget
- **Edit**: Click pencil icon to modify widget configuration

### Global Filters

Global filters affect all widgets on the dashboard:

1. Add a Filter Widget to your dashboard
2. Configure filter:
   - **Field**: Select dimension to filter (e.g., Category, Region)
   - **Operator**: Choose how to filter (Equals, Contains, Greater than, etc.)
   - **Value**: Enter filter value
3. All compatible widgets will automatically apply the filter

### Dashboard Actions

- **Save**: Click "Save" button to persist changes
- **Share**: Click "Share" to get shareable link (requires permissions)
- **Export**: Export entire dashboard as PDF (coming soon)
- **Refresh**: Click refresh icon to reload all widget data

---

## Query Builder

The Query Builder lets you explore data without writing SQL.

### Building a Query

1. Navigate to **Query Builder**
2. Select an **Entity** from dropdown (e.g., "Customer", "Order")
3. **Add Dimensions** (categorical fields):
   - Drag from left panel or click "+" button
   - Examples: Category, Region, Customer Name
4. **Add Measures** (numeric metrics):
   - Drag from left panel or click "+" button
   - Examples: Sales, Profit, Quantity
   - Choose aggregation: SUM, AVG, COUNT, MIN, MAX
5. **Apply Filters** (optional):
   - Click "Add Filter"
   - Select field, operator, and value
   - Example: `Sales > 1000`
6. **Set Limit** (optional):
   - Default: 1000 rows
   - Increase for larger datasets
7. Click **"Run Query"**

### Query Results

Results appear in three views:

**Table View**:
- Sortable columns (click header)
- Pagination controls
- Row count display

**Chart View**:
- Automatic chart based on query
- Switch chart types with dropdown
- Configure sorting and colors (see Chart Visualizations)

**SQL View**:
- Generated SQL query
- Copy button for reuse
- Useful for understanding data model

### Saving Queries

1. Run a query successfully
2. Click **"Save Query"** button
3. Enter:
   - **Name**: Descriptive query name
   - **Description**: What this query shows
4. Access saved queries from dropdown
5. Modify and re-save as needed

### Query Examples

**Example 1: Sales by Category**
- Entity: `Order`
- Dimensions: `Category`
- Measures: `Sales` (SUM)
- Sort: `Sales` descending
- Chart: Bar Chart

**Example 2: Monthly Revenue Trend**
- Entity: `Order`
- Dimensions: `Order Month`
- Measures: `Sales` (SUM)
- Sort: `Order Month` ascending
- Chart: Line Chart

**Example 3: Top 10 Customers**
- Entity: `Customer`
- Dimensions: `Customer Name`
- Measures: `Sales` (SUM)
- Filter: `Sales > 5000`
- Limit: 10
- Sort: `Sales` descending

---

## Chart Visualizations

### Available Chart Types

| Chart Type | Best For | Example Use Case |
|------------|----------|------------------|
| **Bar Chart** | Comparing categories | Sales by Product Category |
| **Horizontal Bar** | Long category names | Sales by Customer Name |
| **Grouped Bar** | Multi-series comparison | Sales vs Profit by Category |
| **Stacked Bar** | Part-to-whole comparison | Sales breakdown by Sub-Category |
| **Line Chart** | Trends over time | Monthly Revenue Growth |
| **Area Chart** | Cumulative trends | Total Sales Over Time |
| **Pie Chart** | Proportions | Market Share by Category |
| **Donut Chart** | Proportions with center metric | Revenue Distribution |
| **Scatter Plot** | Correlation analysis | Sales vs Profit relationship |
| **Heatmap** | Matrix data | Sales by Region and Quarter |
| **Gauge Chart** | Single KPI | Current Month Sales Target |
| **Funnel Chart** | Conversion tracking | Sales Pipeline Stages |

### Configuring Charts

**1. Chart Type Selection**
- Click chart type dropdown
- Preview appears on hover
- Chart updates instantly

**2. Sorting Data**

Sort by dimension:
- Click "Sort Config" panel
- Select field to sort by
- Choose "Ascending" or "Descending"
- Example: Sort categories alphabetically A-Z

Sort by measure:
- Select measure field (e.g., Sales)
- Choose "Descending" to show highest first
- Useful for "Top N" views

**3. Conditional Colors**

Apply color rules based on values:

1. Click "Color Config" panel
2. Click "+ Add Color Rule"
3. Configure rule:
   - **Field**: Select measure (e.g., Profit)
   - **Operator**: >, <, >=, <=, =, !=
   - **Value**: Threshold (e.g., 0)
   - **Color**: Choose color (#FF0000 for red)
4. Add multiple rules:
   - Green for Profit > 1000
   - Yellow for Profit between 0 and 1000
   - Red for Profit < 0

**Example**: Traffic light colors for performance
- Profit > 5000 → Green (#00FF00)
- Profit between 0 and 5000 → Yellow (#FFFF00)
- Profit < 0 → Red (#FF0000)

**4. Advanced Options**

- **Show Legend**: Toggle legend visibility
- **Show Grid Lines**: Toggle grid display
- **Axis Labels**: Customize X/Y axis titles
- **Data Labels**: Show values on chart elements
- **Tooltips**: Hover information (always enabled)

### Exporting Charts

**Export as Image (PNG)**:
1. Right-click chart
2. Select "Save as Image"
3. PNG file downloads with chart name

**Export Data**:
1. Click "Export" dropdown below chart
2. Choose format:
   - **Excel (.xlsx)**: Formatted spreadsheet
   - **CSV (.csv)**: Plain text data
   - **JSON (.json)**: Structured data
3. File downloads immediately

---

## Scheduled Reports & Alerts

**Status**: Backend complete (Week 3 Day 2), Frontend coming in Week 4

Automated report delivery and data monitoring system.

### Email Configuration

Before scheduling reports, configure your SMTP settings:

1. Navigate to **Settings → Email Configuration**
2. Choose provider or use custom SMTP:

**Option A: Use Preset (Recommended)**
- Click preset button: Gmail, Outlook, Office365, Yahoo
- Auto-fills SMTP host and port
- Enter your email and password
- For Gmail: Use App Password (not regular password)

**Option B: Custom SMTP**
- **SMTP Host**: Your mail server (e.g., smtp.gmail.com)
- **SMTP Port**: Usually 587 (TLS) or 465 (SSL)
- **Use TLS**: Enable for port 587
- **Use SSL**: Enable for port 465
- **Username**: Your email address
- **Password**: SMTP password (encrypted before storage)
- **From Email**: Sender email address
- **From Name**: Display name (e.g., "BI Reports")

3. Click **"Test Connection"**
4. Check your email for test message
5. Click **"Save Configuration"**

**Security Note**: Your SMTP password is encrypted using Fernet encryption and never exposed via API.

### Creating Scheduled Reports

1. Navigate to **Scheduled Reports**
2. Click **"New Report"**
3. Configure report:

**Step 1: Basic Information**
- **Name**: Report name (e.g., "Daily Sales Summary")
- **Description**: What this report contains

**Step 2: Data Source**
- Choose one:
  - **Dashboard**: Select existing dashboard to report
  - **Saved Query**: Select saved query to report
- Preview data to verify

**Step 3: Schedule**
- **Type**: Daily, Weekly, or Monthly
- **Time**: 24-hour format (e.g., 09:00 for 9 AM)
- **Day** (Weekly): Monday=0, Sunday=6
- **Day** (Monthly): 1-31 (last day if month shorter)

Schedule examples:
- Daily at 8 AM: `Daily, 08:00`
- Every Monday at 9 AM: `Weekly, 09:00, Day=0`
- 1st of month at 7 AM: `Monthly, 07:00, Day=1`

**Step 4: Recipients & Delivery**
- **Recipients**: Add email addresses (one per line)
- **Formats**: Select file formats to attach:
  - ☑ Excel (.xlsx) - Recommended
  - ☑ CSV (.csv) - For data import
  - ☑ PDF (.pdf) - For viewing
  - ☐ HTML Email - Data embedded in email body
- **Email Subject**: Customize subject line
  - Use `{{date}}` placeholder for current date
  - Example: "Daily Sales Report - {{date}}"
- **Email Body**: Custom message (HTML supported)

**Step 5: Review & Activate**
- Review all settings
- Click **"Create Report"**
- Toggle "Active" switch to enable

4. Report will run automatically on schedule

### Managing Scheduled Reports

**View Reports**:
- See all your scheduled reports in list view
- Columns: Name, Source, Schedule, Recipients, Next Run, Status

**Edit Report**:
- Click pencil icon
- Modify any settings
- Next run time recalculates if schedule changes
- Click "Save"

**Manual Trigger**:
- Click "Run Now" button
- Report executes immediately
- Doesn't affect next scheduled run

**Test Report**:
- Click "Test" button
- Sends to your email only (ignores recipient list)
- Subject prefixed with "[TEST]"
- Useful for verifying before enabling

**View Execution History**:
- Click "History" button
- See past executions with:
  - Status: Success, Failed, Partial
  - Execution time (ms)
  - Row count
  - Files generated
  - Recipients
  - Error messages (if failed)
- Download generated files from history

**Deactivate**:
- Toggle "Active" switch to off
- Report won't run automatically
- Can reactivate anytime

**Delete**:
- Click trash icon
- Confirms deletion
- Removes report and all execution history

### Understanding Report Status

| Status | Meaning | What Happened |
|--------|---------|---------------|
| **Success** | ✓ Complete | Query ran, files generated, email sent |
| **Failed** | ✗ Error | Query or file generation failed |
| **Partial** | ⚠ Warning | Files generated but email failed to send |
| **Running** | ⟳ In Progress | Currently executing |
| **Queued** | ⏳ Waiting | Queued in task system |

### Alerts (Coming in Week 5)

Monitor data and get notified when conditions are met.

**Alert Types**:

1. **Threshold Alert**: Value crosses threshold
   - Example: "Alert when Sales < $10,000"

2. **Change Alert**: Value changes by percentage
   - Example: "Alert when Profit drops 20% from yesterday"

3. **Anomaly Alert**: Statistical outlier detected
   - Uses Z-score analysis
   - Example: "Alert when Daily Sales is abnormal"

4. **Data Quality Alert**: Data issues detected
   - Example: "Alert when NULL values > 5%"

**Creating an Alert**:
1. Select saved query
2. Choose alert type
3. Configure condition (threshold, percentage, etc.)
4. Set check frequency (hourly, daily, etc.)
5. Add recipients
6. Activate alert

---

## Semantic Catalog

The Semantic Catalog is a business-friendly data dictionary.

### Understanding Entities

**Entities** are logical business concepts:
- Customer: Customer information and metrics
- Order: Sales transactions
- Product: Product catalog and performance
- Inventory: Stock levels

Each entity maps to one or more database tables.

### Browsing the Catalog

1. Navigate to **Catalog**
2. See all available entities
3. Click entity name to expand
4. View:
   - **Dimensions**: Categorical fields for grouping
   - **Measures**: Numeric metrics for analysis
   - **Relationships**: Connections to other entities

### Understanding Dimensions

**Dimensions** are attributes for slicing data:
- Customer Name, Region, Segment
- Product Category, Sub-Category
- Order Date, Ship Mode

Properties:
- **Display Name**: Business-friendly name
- **SQL Expression**: Database column or calculation
- **Data Type**: String, Date, Number, Boolean

### Understanding Measures

**Measures** are numeric metrics:
- Sales, Profit, Quantity
- Discount, Shipping Cost
- Customer Count, Order Count

Properties:
- **Display Name**: Business-friendly name
- **Aggregation**: SUM, AVG, COUNT, MIN, MAX
- **SQL Expression**: Column or calculation
- **Format**: Currency, Percentage, Number

**Example Measures**:
- `Total Sales` = SUM(sales)
- `Average Discount` = AVG(discount)
- `Order Count` = COUNT(order_id)
- `Profit Margin` = SUM(profit) / SUM(sales) * 100

### Using the Catalog

The catalog powers:
- **Query Builder**: Select dimensions and measures
- **Dashboard Widgets**: Choose fields for charts
- **Scheduled Reports**: Data available for reporting
- **Alerts**: Metrics to monitor

### Creating Custom Entities (Admin)

1. Use API endpoint `/api/semantic/entities`
2. Define:
   - Entity name and description
   - Primary table
   - SQL definition (optional for complex queries)
3. Add dimensions and measures
4. Mark as "Certified" when validated

See [SEMANTIC_CATALOG_GUIDE.md](SEMANTIC_CATALOG_GUIDE.md) for detailed instructions.

---

## Data Sources

### Supported Connectors

| Type | Description | File Extensions |
|------|-------------|-----------------|
| **CSV** | Comma-separated values | .csv |
| **Excel** | Excel workbooks | .xlsx, .xls |
| **PostgreSQL** | PostgreSQL database | N/A |
| **MySQL** | MySQL database | N/A |

### Adding a CSV File

1. Navigate to **Data Sources**
2. Click **"Add Data Source"**
3. Select **"CSV File"**
4. Upload file:
   - Drag and drop, or click to browse
   - Max file size: 100 MB
5. Configure:
   - **Name**: Display name for this data source
   - **Description**: What the data contains
6. Click **"Upload"**
7. Data is imported to DuckDB for fast querying

### Adding an Excel File

1. Click **"Add Data Source"**
2. Select **"Excel"**
3. Upload .xlsx file
4. Select sheet:
   - If multiple sheets, choose which to import
5. Configure and upload

### Connecting to PostgreSQL

1. Click **"Add Data Source"**
2. Select **"PostgreSQL"**
3. Enter connection details:
   - **Host**: Database server (e.g., localhost)
   - **Port**: Usually 5432
   - **Database**: Database name
   - **Username**: Database user
   - **Password**: User password (encrypted)
   - **Schema**: Usually "public"
4. Click **"Test Connection"**
5. If successful, click **"Save"**

**Security**: Database credentials are encrypted using Fernet encryption before storage.

### Connecting to MySQL

1. Click **"Add Data Source"**
2. Select **"MySQL"**
3. Enter connection details (similar to PostgreSQL)
4. Default port: 3306
5. Test and save

### Managing Data Sources

**View Sources**:
- See all connected data sources
- Status indicator (Connected/Error)

**Refresh Schema**:
- Click refresh icon
- Updates table and column metadata
- Run after database schema changes

**Test Connection**:
- Verifies credentials still work
- Shows connection status

**Edit**:
- Update connection details
- Re-enter password if changed

**Delete**:
- Removes data source
- WARNING: Deletes associated transformations and queries
- Confirm deletion

---

## Data Transformations

Create visual data pipelines without SQL.

### Transformation Steps

Available transformation types:

1. **Filter**: Keep rows matching conditions
2. **Join**: Combine data from multiple tables
3. **Aggregate**: Group and summarize data
4. **Select Columns**: Choose which columns to keep
5. **Rename Columns**: Change column names
6. **Add Calculated Column**: Create new fields with expressions
7. **Sort**: Order data by columns
8. **Deduplicate**: Remove duplicate rows

### Creating a Transformation

1. Navigate to **Transformations**
2. Click **"New Transformation"**
3. Select source data source
4. Add steps:
   - Click "+ Add Step"
   - Choose step type
   - Configure parameters
5. Preview results after each step
6. Save transformation

### Example: Sales Summary

Create a transformation to summarize monthly sales:

**Step 1: Select Source**
- Source: `Superstore` table

**Step 2: Filter**
- Condition: `Order Date >= 2024-01-01`

**Step 3: Add Calculated Column**
- Name: `Order Month`
- Expression: `DATE_TRUNC('month', order_date)`

**Step 4: Aggregate**
- Group By: `Order Month`, `Category`
- Aggregations:
  - Total Sales = SUM(sales)
  - Total Profit = SUM(profit)
  - Order Count = COUNT(order_id)

**Step 5: Sort**
- Column: `Order Month`
- Direction: Ascending

### Reusing Transformations

Saved transformations can be:
- Used as entities in semantic layer
- Queried in Query Builder
- Visualized in dashboards
- Included in scheduled reports

---

## User Management

### User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access, user management, system config |
| **Analyst** | Create dashboards, queries, reports |
| **Viewer** | View dashboards, run queries (no edit) |

### Changing Your Password

1. Click your profile icon (top right)
2. Select **"Profile Settings"**
3. Click **"Change Password"**
4. Enter:
   - Current password
   - New password
   - Confirm new password
5. Click **"Update"**

### Viewing Your Activity

1. Go to **Profile Settings**
2. Click **"Activity Log"**
3. See recent:
   - Queries executed
   - Dashboards viewed
   - Reports generated
   - Login history

---

## Data Export

### Export Formats

**Excel (.xlsx)**:
- Formatted spreadsheet
- Headers in bold
- Column auto-sizing
- Multiple sheets (for dashboards)
- Best for: Sharing with business users

**CSV (.csv)**:
- Plain text, comma-separated
- Universal compatibility
- No formatting
- Best for: Data import to other tools

**JSON (.json)**:
- Structured data format
- Nested objects supported
- Best for: API integration, developers

**PNG (Charts only)**:
- Image of chart
- High resolution
- Best for: Reports, presentations

### Exporting Query Results

1. Run a query in Query Builder
2. Click **"Export"** dropdown
3. Select format
4. File downloads automatically
5. Naming: `query_results_YYYY-MM-DD_HHMMSS.format`

### Exporting Dashboards

1. Open dashboard
2. Click **"Export Dashboard"**
3. Entire dashboard exported as PDF
4. Includes all widgets
5. Coming in future update: Excel workbook with sheets

### Exporting Charts

**Method 1: Right-click**
- Right-click chart
- Select "Save as Image"
- PNG downloads

**Method 2: Export button**
- Click export icon on chart widget
- Choose format
- Downloads immediately

---

## Tips & Best Practices

### Query Builder Tips

**Performance**:
- Use filters to reduce data size
- Set reasonable limits (1000-10000 rows)
- Avoid `SELECT *` - choose specific columns
- Add indexes to frequently filtered columns

**Accuracy**:
- Check aggregation type (SUM vs AVG vs COUNT)
- Verify filter logic (AND vs OR)
- Preview data before saving
- Name queries descriptively

### Dashboard Design

**Layout**:
- Put key metrics at top (KPIs in gauge charts)
- Group related widgets
- Use consistent chart types for similar data
- Leave white space - don't overcrowd

**Filters**:
- Add global filters at top
- Limit to 3-5 filters (avoid overwhelming users)
- Set sensible defaults
- Label filters clearly

**Performance**:
- Limit widgets per dashboard to 6-8
- Use cached queries when possible
- Avoid real-time refresh unless needed
- Test with full dataset before sharing

### Chart Selection

**Choose charts based on data type**:

| Data Pattern | Best Chart |
|--------------|------------|
| Compare categories | Bar Chart |
| Show trend over time | Line Chart |
| Show proportions | Pie/Donut Chart |
| Find correlation | Scatter Plot |
| Show distribution | Histogram |
| Compare multiple series | Grouped/Stacked Bar |
| Show ranking | Horizontal Bar |
| Show progress to goal | Gauge Chart |
| Show conversion funnel | Funnel Chart |

### Scheduled Reports

**Best Practices**:
- Test reports before scheduling
- Use clear, descriptive names
- Schedule during off-peak hours
- Limit recipients (use distribution lists)
- Include context in email body
- Monitor execution history for failures

**Troubleshooting**:
- Check SMTP configuration if emails fail
- Verify saved query still works
- Check recipient email addresses
- Review error messages in history
- Test connection before large rollouts

### Security

**Passwords**:
- Use strong passwords (12+ characters)
- Change default admin password immediately
- Don't share credentials
- Use app passwords for Gmail (not regular password)

**Data Access**:
- Only grant necessary permissions
- Review user access periodically
- Remove inactive users
- Audit sensitive data access

**Email Reports**:
- Use encryption for sensitive data
- Verify recipient list before scheduling
- Don't email to external addresses unless approved
- Monitor execution history for unauthorized access

### Performance Optimization

**Large Datasets**:
- Use filters to reduce data
- Create pre-aggregated tables
- Index frequently queried columns
- Limit dashboard complexity

**Slow Queries**:
- Add database indexes
- Use aggregations in semantic layer
- Cache frequently used results
- Optimize SQL expressions

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Save dashboard | Ctrl + S |
| Run query | Ctrl + Enter |
| Open search | Ctrl + K |
| Toggle fullscreen | F11 |
| Refresh data | F5 |
| Undo | Ctrl + Z |
| Redo | Ctrl + Y |

---

## Getting Help

### Resources

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **User Manual**: This document
- **Video Tutorials**: Coming soon
- **FAQ**: See project wiki

### Common Issues

**Can't login?**
- Check credentials
- Verify backend is running (port 8000)
- Clear browser cache

**Query not running?**
- Check data source connection
- Verify entity exists in catalog
- Review query syntax in SQL view

**Chart not displaying?**
- Ensure query returned data
- Check chart type is appropriate for data
- Try different chart type

**Report not sending?**
- Test email configuration
- Check SMTP credentials
- Verify recipient emails
- Review execution history for error

### Support

For bugs or feature requests:
- GitHub Issues: [https://github.com/pssambila-maker/BIApp/issues](https://github.com/pssambila-maker/BIApp/issues)
- Email: support@example.com

---

**End of User Manual**

*Last updated: January 12, 2026*
*Version: 1.0*
*For application version: Phase 9 (Week 3 Day 2)*
