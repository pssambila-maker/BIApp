# Phase 4: Semantic Layer - Testing Guide

This guide walks you through testing the semantic layer functionality (Phase 4 Foundation).

## Prerequisites

✅ Backend server running on http://localhost:8000
✅ PostgreSQL database with Phase 1-4 migrations applied
✅ Valid authentication token

---

## Part 1: Create Customer Entity with Dimensions and Measures

### Step 1: Login and Get Token

Follow steps from the main TESTING_GUIDE.md to login and get your access token.

### Step 2: Create Customer Entity

**Endpoint**: `POST /api/semantic/entities`

**Request Body**:
```json
{
  "name": "Customer",
  "plural_name": "Customers",
  "description": "Customer master data and metrics",
  "primary_table": "customers",
  "is_certified": true,
  "tags": ["master-data", "sales", "core"]
}
```

**Expected Response** (201 Created):
```json
{
  "id": "uuid-here",
  "name": "Customer",
  "plural_name": "Customers",
  "description": "Customer master data and metrics",
  "primary_table": "customers",
  "sql_definition": null,
  "is_certified": true,
  "tags": ["master-data", "sales", "core"],
  "owner_id": "your-user-id",
  "created_at": "2026-01-07T...",
  "updated_at": "2026-01-07T...",
  "dimensions": [],
  "measures": []
}
```

**IMPORTANT**: Copy the entity `id` - you'll need it for the next steps!

---

### Step 3: Add Dimensions to Customer Entity

#### Dimension 1: Customer Name

**Endpoint**: `POST /api/semantic/entities/{entity_id}/dimensions`

**Request Body**:
```json
{
  "name": "Customer Name",
  "description": "Full customer name",
  "sql_column": "full_name",
  "data_type": "string",
  "display_format": "title_case",
  "is_hidden": false,
  "display_order": 0
}
```

**Expected Response** (201 Created):
```json
{
  "id": "dimension-uuid",
  "semantic_entity_id": "entity-uuid",
  "name": "Customer Name",
  "description": "Full customer name",
  "sql_column": "full_name",
  "data_type": "string",
  "display_format": "title_case",
  "is_hidden": false,
  "display_order": 0,
  "created_at": "2026-01-07T...",
  "updated_at": "2026-01-07T..."
}
```

#### Dimension 2: Region

**Endpoint**: `POST /api/semantic/entities/{entity_id}/dimensions`

**Request Body**:
```json
{
  "name": "Region",
  "description": "Customer geographic region",
  "sql_column": "region",
  "data_type": "string",
  "display_format": "uppercase",
  "is_hidden": false,
  "display_order": 1
}
```

#### Dimension 3: Signup Date

**Endpoint**: `POST /api/semantic/entities/{entity_id}/dimensions`

**Request Body**:
```json
{
  "name": "Signup Date",
  "description": "When the customer signed up",
  "sql_column": "created_at",
  "data_type": "date",
  "display_format": "date_format:YYYY-MM-DD",
  "is_hidden": false,
  "display_order": 2
}
```

#### Dimension 4: Is Active (Boolean Example)

**Endpoint**: `POST /api/semantic/entities/{entity_id}/dimensions`

**Request Body**:
```json
{
  "name": "Is Active",
  "description": "Whether customer is currently active",
  "sql_column": "is_active",
  "data_type": "boolean",
  "is_hidden": false,
  "display_order": 3
}
```

---

### Step 4: Add Measures to Customer Entity

#### Measure 1: Customer Count

**Endpoint**: `POST /api/semantic/entities/{entity_id}/measures`

**Request Body**:
```json
{
  "name": "Customer Count",
  "description": "Total number of customers",
  "aggregation_function": "COUNT",
  "base_column": "id",
  "format": "integer",
  "default_format_pattern": "#,##0",
  "is_hidden": false
}
```

**Expected Response** (201 Created):
```json
{
  "id": "measure-uuid",
  "semantic_entity_id": "entity-uuid",
  "name": "Customer Count",
  "description": "Total number of customers",
  "calculation_type": "aggregation",
  "aggregation_function": "COUNT",
  "base_column": "id",
  "format": "integer",
  "default_format_pattern": "#,##0",
  "is_hidden": false,
  "created_at": "2026-01-07T...",
  "updated_at": "2026-01-07T..."
}
```

#### Measure 2: Total Revenue

**Endpoint**: `POST /api/semantic/entities/{entity_id}/measures`

**Request Body**:
```json
{
  "name": "Total Revenue",
  "description": "Sum of all customer revenue",
  "aggregation_function": "SUM",
  "base_column": "total_spent",
  "format": "currency",
  "default_format_pattern": "$#,##0.00",
  "is_hidden": false
}
```

#### Measure 3: Average Order Value

**Endpoint**: `POST /api/semantic/entities/{entity_id}/measures`

**Request Body**:
```json
{
  "name": "Average Order Value",
  "description": "Average amount spent per customer",
  "aggregation_function": "AVG",
  "base_column": "total_spent",
  "format": "currency",
  "default_format_pattern": "$#,##0.00",
  "is_hidden": false
}
```

---

## Part 2: Create Product Entity

### Step 5: Create Product Entity

**Endpoint**: `POST /api/semantic/entities`

**Request Body**:
```json
{
  "name": "Product",
  "plural_name": "Products",
  "description": "Product catalog and sales metrics",
  "primary_table": "products",
  "is_certified": false,
  "tags": ["catalog", "sales"]
}
```

### Step 6: Add Product Dimensions

#### Product Name
```json
{
  "name": "Product Name",
  "description": "Product display name",
  "sql_column": "product_name",
  "data_type": "string",
  "display_format": "title_case",
  "display_order": 0
}
```

#### Category
```json
{
  "name": "Category",
  "description": "Product category",
  "sql_column": "category",
  "data_type": "string",
  "display_format": "title_case",
  "display_order": 1
}
```

#### Unit Price
```json
{
  "name": "Unit Price",
  "description": "Base price per unit",
  "sql_column": "unit_price",
  "data_type": "decimal",
  "display_format": "currency",
  "display_order": 2
}
```

### Step 7: Add Product Measures

#### Units Sold
```json
{
  "name": "Units Sold",
  "description": "Total units sold",
  "aggregation_function": "SUM",
  "base_column": "quantity_sold",
  "format": "integer",
  "default_format_pattern": "#,##0"
}
```

#### Product Count
```json
{
  "name": "Product Count",
  "description": "Number of distinct products",
  "aggregation_function": "COUNT",
  "base_column": "id",
  "format": "integer",
  "default_format_pattern": "#,##0"
}
```

---

## Part 3: Retrieve and Manage Entities

### Step 8: List All Entities

**Endpoint**: `GET /api/semantic/entities`

**Expected Response** (200 OK):
```json
[
  {
    "id": "customer-uuid",
    "name": "Customer",
    "plural_name": "Customers",
    "description": "Customer master data and metrics",
    "primary_table": "customers",
    "is_certified": true,
    "tags": ["master-data", "sales", "core"],
    "dimension_count": 4,
    "measure_count": 3,
    "created_at": "2026-01-07T...",
    "updated_at": "2026-01-07T..."
  },
  {
    "id": "product-uuid",
    "name": "Product",
    "plural_name": "Products",
    "description": "Product catalog and sales metrics",
    "primary_table": "products",
    "is_certified": false,
    "tags": ["catalog", "sales"],
    "dimension_count": 3,
    "measure_count": 2,
    "created_at": "2026-01-07T...",
    "updated_at": "2026-01-07T..."
  }
]
```

### Step 9: Get Specific Entity with Dimensions and Measures

**Endpoint**: `GET /api/semantic/entities/{entity_id}`

**Expected Response** (200 OK):
Full entity with all dimensions and measures arrays populated.

### Step 10: List Dimensions for an Entity

**Endpoint**: `GET /api/semantic/entities/{entity_id}/dimensions`

**Expected Response** (200 OK):
Array of dimensions ordered by `display_order` then `name`.

### Step 11: List Measures for an Entity

**Endpoint**: `GET /api/semantic/entities/{entity_id}/measures`

**Expected Response** (200 OK):
Array of measures ordered by `name`.

---

## Part 4: Get Complete Semantic Catalog (Priority Feature)

### Step 12: Retrieve Semantic Catalog

**Endpoint**: `GET /api/semantic/catalog`

**Expected Response** (200 OK):
```json
{
  "entities": [
    {
      "id": "customer-uuid",
      "name": "Customer",
      "plural_name": "Customers",
      "description": "Customer master data and metrics",
      "primary_table": "customers",
      "is_certified": true,
      "tags": ["master-data", "sales", "core"],
      "dimensions": [
        {
          "id": "dim-uuid-1",
          "name": "Customer Name",
          "description": "Full customer name",
          "sql_column": "full_name",
          "data_type": "string",
          "display_format": "title_case",
          "is_hidden": false,
          "display_order": 0,
          ...
        },
        ...
      ],
      "measures": [
        {
          "id": "meas-uuid-1",
          "name": "Customer Count",
          "description": "Total number of customers",
          "calculation_type": "aggregation",
          "aggregation_function": "COUNT",
          "base_column": "id",
          "format": "integer",
          ...
        },
        ...
      ]
    },
    {
      "id": "product-uuid",
      "name": "Product",
      ...
    }
  ],
  "total_entities": 2,
  "total_dimensions": 7,
  "total_measures": 5
}
```

**This is the key endpoint for frontend consumption!**

---

## Part 5: Update Operations

### Step 13: Update an Entity

**Endpoint**: `PUT /api/semantic/entities/{entity_id}`

**Request Body** (partial update):
```json
{
  "description": "Updated: Customer master data with complete metrics",
  "is_certified": false,
  "tags": ["master-data", "sales", "core", "revenue"]
}
```

**Expected Response** (200 OK): Updated entity with new values

### Step 14: Update a Dimension

**Endpoint**: `PUT /api/semantic/dimensions/{dimension_id}`

**Request Body**:
```json
{
  "display_order": 5,
  "is_hidden": true
}
```

**Expected Response** (200 OK): Updated dimension

### Step 15: Update a Measure

**Endpoint**: `PUT /api/semantic/measures/{measure_id}`

**Request Body**:
```json
{
  "format": "decimal",
  "default_format_pattern": "#,##0.000"
}
```

**Expected Response** (200 OK): Updated measure

---

## Part 6: Validation Testing

### Step 16: Test Invalid Data Type (Should Fail)

**Endpoint**: `POST /api/semantic/entities/{entity_id}/dimensions`

**Request Body**:
```json
{
  "name": "Test Dimension",
  "sql_column": "test_col",
  "data_type": "invalid_type",
  "display_order": 0
}
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "data_type"],
      "msg": "String should match pattern '^(string|integer|date|boolean|decimal)$'",
      "type": "string_pattern_mismatch"
    }
  ]
}
```

### Step 17: Test Invalid Aggregation Function (Should Fail)

**Endpoint**: `POST /api/semantic/entities/{entity_id}/measures`

**Request Body**:
```json
{
  "name": "Test Measure",
  "aggregation_function": "INVALID",
  "base_column": "test_col"
}
```

**Expected Response** (422 Unprocessable Entity):
Validation error for aggregation_function pattern

### Step 18: Test Invalid Tags (Should Fail)

**Endpoint**: `POST /api/semantic/entities`

**Request Body**:
```json
{
  "name": "Test Entity",
  "primary_table": "test_table",
  "tags": ["valid", 123, "invalid"]
}
```

**Expected Response** (422 Unprocessable Entity):
Validation error - all tags must be strings

---

## Part 7: Delete Operations

### Step 19: Delete a Dimension

**Endpoint**: `DELETE /api/semantic/dimensions/{dimension_id}`

**Expected Response** (204 No Content)

Verify deletion:
- `GET /api/semantic/entities/{entity_id}/dimensions` should show one less dimension
- Dimension count in entity list should decrease

### Step 20: Delete a Measure

**Endpoint**: `DELETE /api/semantic/measures/{measure_id}`

**Expected Response** (204 No Content)

Verify deletion similar to dimensions.

### Step 21: Delete an Entity (Cascades)

**Endpoint**: `DELETE /api/semantic/entities/{entity_id}`

**Expected Response** (204 No Content)

**Verify Cascade**:
- Entity is deleted
- All associated dimensions are deleted
- All associated measures are deleted
- `GET /api/semantic/catalog` should show one less entity

---

## Part 8: Ownership Testing

### Step 22: Test Cross-User Access

1. **Create entity as User A**
2. **Login as User B** (different user)
3. **Try to access User A's entity**:
   - `GET /api/semantic/entities/{user_a_entity_id}`
   - **Expected**: 404 Not Found (entity doesn't exist for User B)
4. **Try to update User A's entity**:
   - `PUT /api/semantic/entities/{user_a_entity_id}`
   - **Expected**: 404 Not Found
5. **Try to delete User A's entity**:
   - `DELETE /api/semantic/entities/{user_a_entity_id}`
   - **Expected**: 404 Not Found

**This verifies proper ownership isolation.**

---

## Expected Results Summary

After completing all steps, you should have:

✅ **Created 2 Entities** - Customer and Product
✅ **Added 7 Dimensions** - Various data types (string, date, boolean, decimal)
✅ **Added 5 Measures** - Various aggregation functions (SUM, COUNT, AVG)
✅ **Retrieved Catalog** - Complete semantic model with all entities
✅ **Updated Entities/Dimensions/Measures** - Modified existing objects
✅ **Validated Input** - Confirmed enum validation works
✅ **Deleted Resources** - Verified cascade deletes work
✅ **Tested Ownership** - Confirmed cross-user isolation

---

## Validation Rules Reference

### Data Types (dimensions)
- `string` - Text data
- `integer` - Whole numbers
- `date` - Date values
- `boolean` - True/False
- `decimal` - Decimal numbers

### Aggregation Functions (measures)
- `SUM` - Sum of values
- `COUNT` - Count of rows
- `AVG` - Average value
- `MIN` - Minimum value
- `MAX` - Maximum value
- `MEDIAN` - Median value
- `STDDEV` - Standard deviation

### Display Formats (dimensions)
- `title_case` - Title Case
- `uppercase` - UPPERCASE
- `date_format:YYYY-MM-DD` - Date formatting

### Display Formats (measures)
- `currency` - Monetary values
- `percent` - Percentage values
- `integer` - Whole numbers
- `decimal` - Decimal numbers

---

## Catalog Endpoint Usage

The **catalog endpoint** (`GET /api/semantic/catalog`) is the primary interface for frontend applications to discover available semantic objects.

**Use cases**:
1. **Metric Browser**: Frontend displays all available metrics users can add to dashboards
2. **Dimension Selector**: Show all dimensions available for filtering/grouping
3. **Data Dictionary**: Browse and search semantic definitions
4. **Autocomplete**: Suggest dimensions and measures in query builders
5. **Validation**: Check if referenced semantic objects exist

**Frontend Implementation Example**:
```javascript
// Fetch catalog on app load
const catalog = await fetch('/api/semantic/catalog', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Build dimension picker
const dimensions = catalog.entities.flatMap(e =>
  e.dimensions.map(d => ({
    entityName: e.name,
    ...d
  }))
);

// Build measure picker
const measures = catalog.entities.flatMap(e =>
  e.measures.map(m => ({
    entityName: e.name,
    ...m
  }))
);
```

---

## Troubleshooting

### Issue: "Entity not found" when accessing dimensions/measures
**Solution**: Verify the entity belongs to the current authenticated user. Entities are isolated by owner_id.

### Issue: Validation error on data_type
**Solution**: Use only allowed values: string, integer, date, boolean, decimal

### Issue: Validation error on aggregation_function
**Solution**: Use only allowed values: SUM, COUNT, AVG, MIN, MAX, MEDIAN, STDDEV

### Issue: Tags validation fails
**Solution**: Ensure tags is an array of strings, not mixed types

### Issue: Cannot delete entity
**Solution**: Check ownership. You can only delete entities you created.

### Issue: Dimension order doesn't match display_order
**Solution**: Dimensions are ordered by display_order, then name. Check both fields.

---

## Next Steps

Once all Phase 4 tests pass:
- ✅ Semantic layer foundation is complete
- 🎯 Ready for frontend integration (catalog consumption)
- 📊 Ready for Phase 5: Analytics Canvas (visualization builder)
- 📈 Future: Add relationships, calculated fields, hierarchies

---

## Performance Notes

- **Catalog endpoint**: Uses `selectinload` to fetch all data in one query (efficient)
- **Entity list**: Uses SQL aggregation for counts (no N+1 queries)
- **Indexes**: All foreign keys and frequently queried fields are indexed
- **Cascade deletes**: Handled at database level (efficient)

The semantic layer is optimized for read-heavy workloads typical of BI applications.
