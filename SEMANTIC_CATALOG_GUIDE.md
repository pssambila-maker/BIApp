# Semantic Catalog Guide

Complete guide to creating and managing semantic catalogs in the BI Platform.

## Table of Contents
- [What is a Semantic Catalog?](#what-is-a-semantic-catalog)
- [Architecture Overview](#architecture-overview)
- [Creating Semantic Entities](#creating-semantic-entities)
- [Working with Dimensions](#working-with-dimensions)
- [Working with Measures](#working-with-measures)
- [Data Source Integration](#data-source-integration)
- [Query Builder Usage](#query-builder-usage)
- [Best Practices](#best-practices)
- [Examples](#examples)

---

## What is a Semantic Catalog?

The Semantic Catalog is a business-friendly layer that sits on top of your raw data sources. It allows you to:

- **Define business entities** (e.g., Customer, Product, Order)
- **Create business-friendly names** for technical database columns
- **Define metrics and calculations** (e.g., Total Revenue, Average Order Value)
- **Hide technical complexity** from end users
- **Enable self-service analytics** through the Query Builder

### Key Components

1. **Entities**: Business objects (Customer, Product, Order)
2. **Dimensions**: Attributes for grouping and filtering (Customer Name, Region, Category)
3. **Measures**: Numeric metrics that can be aggregated (Sales, Quantity, Profit)
4. **Data Sources**: Underlying database connections (PostgreSQL, CSV, Excel)

---

## Architecture Overview

```
Data Sources (PostgreSQL, CSV, Excel)
         ↓
Data Source Tables (Metadata about tables/files)
         ↓
Semantic Entities (Business objects)
    ├── Dimensions (Grouping/Filtering attributes)
    └── Measures (Numeric metrics)
         ↓
Query Builder (User interface for building queries)
         ↓
Generated SQL + Execution
         ↓
Results (Table view, Charts, Export)
```

---

## Creating Semantic Entities

### Via UI (Recommended)

1. Navigate to **Semantic Catalog** page
2. Click **Create Entity** button
3. Fill in entity details:
   - **Name**: Singular form (e.g., "Customer")
   - **Plural Name**: Plural form (e.g., "Customers")
   - **Description**: Business description
   - **Primary Table**: The main data source table
   - **Tags**: Optional classification tags

4. Add Dimensions and Measures (see sections below)
5. Click **Save**

### Via Python Script

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.semantic import SemanticEntity, SemanticDimension, SemanticMeasure

async def create_entity():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        # Create entity
        entity = SemanticEntity(
            owner_id='user-uuid-here',
            name='Order',
            plural_name='Orders',
            description='Sales orders',
            primary_table='superstore'
        )
        session.add(entity)
        await session.flush()  # Get entity.id

        # Add dimensions (see next section)
        # Add measures (see next section)

        await session.commit()

asyncio.run(create_entity())
```

---

## Working with Dimensions

Dimensions are attributes used for:
- **Grouping data** (GROUP BY in SQL)
- **Filtering data** (WHERE in SQL)
- **Labeling** (axes in charts)

### Common Dimension Types

| Type | Example | Data Type | Use Case |
|------|---------|-----------|----------|
| Text | Customer Name | string | Grouping, filtering |
| Category | Product Category | string | Grouping, filtering |
| Date | Order Date | date | Time-based analysis |
| Location | City, Region | string | Geographic analysis |
| ID | Customer ID | string | Joins, lookups |

### Creating Dimensions via Python

```python
# Text dimension
dim_customer = SemanticDimension(
    semantic_entity_id=entity.id,
    name='Customer Name',
    sql_column='customer_name',  # Actual column in database
    data_type='string',
    is_hidden=False,
    display_order=1
)

# Date dimension
dim_order_date = SemanticDimension(
    semantic_entity_id=entity.id,
    name='Order Date',
    sql_column='order_date',
    data_type='date',
    display_format='%Y-%m-%d',
    is_hidden=False,
    display_order=2
)

# Category dimension
dim_region = SemanticDimension(
    semantic_entity_id=entity.id,
    name='Region',
    sql_column='region',
    data_type='string',
    is_hidden=False,
    display_order=3
)

session.add_all([dim_customer, dim_order_date, dim_region])
```

### Dimension Properties

- **name**: Business-friendly name shown to users
- **sql_column**: Actual column name in the database table
- **data_type**: string, integer, date, boolean
- **display_format**: Format string (for dates, numbers)
- **is_hidden**: Hide from Query Builder if true
- **display_order**: Sort order in UI

---

## Working with Measures

Measures are numeric metrics that can be aggregated (SUM, AVG, COUNT, etc.).

### Common Measure Types

| Aggregation | Example | Use Case |
|-------------|---------|----------|
| SUM | Total Sales | Add up all values |
| AVG | Average Price | Calculate mean |
| COUNT | Number of Orders | Count rows |
| MIN | Minimum Price | Find smallest value |
| MAX | Maximum Price | Find largest value |

### Creating Measures via Python

```python
# Sum measure
measure_sales = SemanticMeasure(
    semantic_entity_id=entity.id,
    name='Total Sales',
    aggregation_function='SUM',
    base_column='sales',  # Column to aggregate
    format='currency',
    default_format_pattern='$#,##0.00',
    is_hidden=False
)

# Count measure
measure_orders = SemanticMeasure(
    semantic_entity_id=entity.id,
    name='Number of Orders',
    aggregation_function='COUNT',
    base_column='order_id',
    format='number',
    default_format_pattern='#,##0',
    is_hidden=False
)

# Average measure
measure_avg_discount = SemanticMeasure(
    semantic_entity_id=entity.id,
    name='Average Discount',
    aggregation_function='AVG',
    base_column='discount',
    format='percent',
    default_format_pattern='0.0%',
    is_hidden=False
)

session.add_all([measure_sales, measure_orders, measure_avg_discount])
```

### Measure Properties

- **name**: Business-friendly name
- **aggregation_function**: SUM, AVG, COUNT, MIN, MAX
- **base_column**: Database column to aggregate
- **format**: currency, number, percent
- **default_format_pattern**: Display format
- **is_hidden**: Hide from Query Builder if true

---

## Data Source Integration

### Prerequisites

Before creating semantic entities, you need:

1. **Data Source**: Connection to PostgreSQL/CSV/Excel
2. **Data Source Tables**: Metadata about tables/files

### Linking Entities to Data Sources

The semantic layer automatically finds the data source by:
1. Looking up `entity.primary_table` (e.g., "superstore")
2. Finding matching table in `data_source_tables`
3. Getting the parent `data_source`
4. Using connection info to query the database

### Creating Data Source Table Metadata

```python
from app.models import DataSource, DataSourceTable

# For PostgreSQL table
ds_table = DataSourceTable(
    data_source_id=data_source.id,
    table_name='superstore',
    schema_name='public',
    column_metadata=[
        {'name': 'order_id', 'type': 'VARCHAR'},
        {'name': 'sales', 'type': 'NUMERIC'},
        # ... more columns
    ],
    row_count=9994,
    size_bytes=1500000
)
session.add(ds_table)
```

### Supported Data Source Types

| Type | Extension | Notes |
|------|-----------|-------|
| PostgreSQL | N/A | Full SQL support |
| MySQL | N/A | Full SQL support |
| CSV | .csv | DuckDB backend |
| Excel | .xlsx | DuckDB backend |

---

## Query Builder Usage

### Building a Query

1. Navigate to **Query Builder** page
2. **Select Entity** from dropdown
3. **Select Dimensions** for grouping (e.g., Region, Category)
4. **Select Measures** to calculate (e.g., Total Sales, Count)
5. **Add Filters** (optional) to narrow results
6. Click **Execute Query**

### Generated SQL Example

**Query Configuration**:
- Entity: Order
- Dimensions: Region
- Measures: Total Sales (SUM)

**Generated SQL**:
```sql
SELECT
    region,
    SUM(sales) as total_sales
FROM superstore
GROUP BY region
LIMIT 1000
```

### Viewing Results

Results are displayed in two views:

1. **Table View**: Raw data in tabular format
   - Export to CSV, Excel, JSON
   - View generated SQL

2. **Chart View**: Visualizations
   - Bar charts
   - Line charts
   - Area charts
   - Pie charts
   - Configure axes and series

### Saving Queries

1. After executing a query, click **Save Query**
2. Provide a name and description
3. Access saved queries from the **Load Query** button
4. View query history from the **History** button

---

## Best Practices

### Naming Conventions

**Entities**:
- Use singular form: "Customer" not "Customers"
- Use business terms, not technical names
- Keep names short but descriptive

**Dimensions**:
- Be specific: "Customer Name" not just "Name"
- Include units if relevant: "Order Date" not "Date"
- Use consistent naming across entities

**Measures**:
- Start with aggregation: "Total Sales" not "Sales Total"
- Include units: "Average Price (USD)"
- Be descriptive: "Number of Orders" not "Count"

### Performance Optimization

1. **Limit Result Sets**: Use appropriate LIMIT values
2. **Index Columns**: Index columns used in dimensions
3. **Aggregate When Possible**: Pre-aggregate large datasets
4. **Use Filters**: Encourage users to filter data
5. **Hide Unused Fields**: Set `is_hidden=True` for technical columns

### Data Quality

1. **Validate Data Types**: Ensure SQL columns match dimension types
2. **Test Queries**: Execute test queries after creating entities
3. **Document Calculations**: Add clear descriptions
4. **Handle NULLs**: Consider NULL values in calculations
5. **Verify Mappings**: Ensure column names match exactly

### Security

1. **Row-Level Security**: Filter data by `owner_id`
2. **Column Permissions**: Hide sensitive dimensions
3. **Audit Logging**: Track query history
4. **Data Source Credentials**: Encrypt connection strings

---

## Examples

### Example 1: Customer Entity

```python
# Entity
entity = SemanticEntity(
    owner_id=user_id,
    name='Customer',
    plural_name='Customers',
    description='Customer master data and metrics',
    primary_table='superstore'
)

# Dimensions
dimensions = [
    SemanticDimension(
        semantic_entity_id=entity.id,
        name='Customer Name',
        sql_column='customer_name',
        data_type='string'
    ),
    SemanticDimension(
        semantic_entity_id=entity.id,
        name='Region',
        sql_column='region',
        data_type='string'
    ),
    SemanticDimension(
        semantic_entity_id=entity.id,
        name='Segment',
        sql_column='segment',
        data_type='string'
    )
]

# Measures
measures = [
    SemanticMeasure(
        semantic_entity_id=entity.id,
        name='Total Orders',
        aggregation_function='COUNT',
        base_column='order_id'
    )
]
```

### Example 2: Product Entity

```python
# Entity
entity = SemanticEntity(
    owner_id=user_id,
    name='Product',
    plural_name='Products',
    description='Product catalog and sales metrics',
    primary_table='superstore'
)

# Dimensions
dimensions = [
    SemanticDimension(
        semantic_entity_id=entity.id,
        name='Product Name',
        sql_column='product_name',
        data_type='string'
    ),
    SemanticDimension(
        semantic_entity_id=entity.id,
        name='Category',
        sql_column='category',
        data_type='string'
    ),
    SemanticDimension(
        semantic_entity_id=entity.id,
        name='Sub-Category',
        sql_column='sub_category',
        data_type='string'
    )
]

# Measures
measures = [
    SemanticMeasure(
        semantic_entity_id=entity.id,
        name='Units Sold',
        aggregation_function='SUM',
        base_column='quantity'
    ),
    SemanticMeasure(
        semantic_entity_id=entity.id,
        name='Total Revenue',
        aggregation_function='SUM',
        base_column='sales',
        format='currency'
    ),
    SemanticMeasure(
        semantic_entity_id=entity.id,
        name='Total Profit',
        aggregation_function='SUM',
        base_column='profit',
        format='currency'
    )
]
```

### Example 3: Complex Query

**Business Question**: "What are the total sales and profit by region and category?"

**Query Configuration**:
- Entity: Product
- Dimensions: Region, Category
- Measures: Total Revenue, Total Profit
- Filter: Order Date >= '2020-01-01'

**Generated SQL**:
```sql
SELECT
    region,
    category,
    SUM(sales) as total_revenue,
    SUM(profit) as total_profit
FROM superstore
WHERE order_date >= '2020-01-01'
GROUP BY region, category
ORDER BY total_revenue DESC
LIMIT 1000
```

---

## Troubleshooting

### Common Issues

**Issue**: "Column not found in table"
- **Solution**: Verify `sql_column` matches exact column name in database
- Use `\d tablename` in psql to see actual column names

**Issue**: "No data source found for table"
- **Solution**: Create `DataSourceTable` entry linking table to data source
- Verify `primary_table` matches `table_name` in `data_source_tables`

**Issue**: "Invalid aggregation function"
- **Solution**: Use only: SUM, AVG, COUNT, MIN, MAX
- Check spelling and case (must be uppercase)

**Issue**: "Query returns no results"
- **Solution**: Check filters, verify data exists
- Test the generated SQL directly in psql

**Issue**: "Chart visualization error"
- **Solution**: Ensure at least one dimension and one measure
- Check that column names in results match configuration

---

## API Reference

### REST Endpoints

```
GET    /api/semantic/catalog          - List all entities
GET    /api/semantic/entities/:id     - Get entity details
POST   /api/semantic/entities         - Create entity
PUT    /api/semantic/entities/:id     - Update entity
DELETE /api/semantic/entities/:id     - Delete entity

POST   /api/query-builder/execute     - Execute query
GET    /api/query-builder/history     - Query history
POST   /api/query-builder/save        - Save query
GET    /api/query-builder/saved       - List saved queries
```

### Python Models

Located in `backend/app/models/semantic.py`:
- `SemanticEntity`
- `SemanticDimension`
- `SemanticMeasure`

---

## Additional Resources

- [PostgreSQL Operations Guide](POSTGRESQL_OPERATIONS.md)
- [Admin User Management Guide](ADMIN_USER_MANAGEMENT.md)
- [Chart Visualization Testing](CHART_VISUALIZATION_TESTING.md)
- Main README for setup instructions
