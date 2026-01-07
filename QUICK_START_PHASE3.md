# Phase 3 Quick Start - Clean Testing Guide

## Prerequisites

Before starting, make sure you have:
1. ✅ Backend server running at http://localhost:8000
2. ✅ Valid access token (from login)
3. ✅ At least one data source created (CSV recommended)

---

## Step 1: Get Your Data Source ID

**Endpoint**: `GET /api/data-sources`

**Expected Response**:
```json
[
  {
    "id": "0856475b-6cfc-43dd-ae4e-b5d9c4d8811b",
    "name": "Sales Data CSV",
    "type": "csv",
    ...
  }
]
```

**IMPORTANT**: Copy the `id` value - you'll need it for the next step!

---

## Step 2: Create Your First Pipeline (Simple Filter)

**Endpoint**: `POST /api/pipelines`

**Request Body** (replace `YOUR_DATA_SOURCE_ID` with the actual UUID from Step 1):

```json
{
  "name": "Simple Sales Filter",
  "description": "Test pipeline - filter high value sales",
  "is_active": true,
  "steps": [
    {
      "step_order": 0,
      "step_type": "source",
      "step_name": "Load Sales Data",
      "configuration": {
        "data_source_id": "YOUR_DATA_SOURCE_ID",
        "table_name": "sales_data"
      },
      "output_alias": "sales"
    },
    {
      "step_order": 1,
      "step_type": "filter",
      "step_name": "High Value Filter",
      "configuration": {
        "conditions": [
          {
            "column": "unit_price",
            "operator": ">",
            "value": 1000
          }
        ],
        "logical_operator": "AND"
      }
    }
  ]
}
```

**Expected Response**: Status 201, with a pipeline ID

**IMPORTANT**: Copy the pipeline `id` for the next step!

---

## Step 3: Execute the Pipeline

**Endpoint**: `POST /api/pipelines/{pipeline_id}/execute`

**Path Parameter**: Use the pipeline ID from Step 2

**Request Body**:
```json
{
  "limit": 100,
  "preview_mode": true
}
```

**Expected Response**: Status 200
```json
{
  "run_id": "...",
  "status": "success",
  "rows_processed": 5,
  "execution_time_seconds": 0.234,
  "data": {
    "columns": ["order_id", "customer_name", "product", "quantity", "unit_price", "region"],
    "rows": [
      {
        "order_id": "001",
        "customer_name": "Acme Corp",
        "product": "Enterprise Laptop",
        "quantity": 3,
        "unit_price": 1200,
        "region": "North"
      }
      // ... more rows
    ]
  },
  "error_message": null
}
```

**If it works**: ✅ Phase 3 is working! Continue to Step 4

**If it fails**: Check the `error_message` field and verify:
- Data source ID is correct
- Table name matches your CSV file
- Column name `unit_price` exists in your data

---

## Step 4: Create an Aggregation Pipeline

**Endpoint**: `POST /api/pipelines`

**Request Body** (replace `YOUR_DATA_SOURCE_ID`):

```json
{
  "name": "Sales by Region",
  "description": "Aggregate sales data by region",
  "is_active": true,
  "steps": [
    {
      "step_order": 0,
      "step_type": "source",
      "step_name": "Load Sales",
      "configuration": {
        "data_source_id": "YOUR_DATA_SOURCE_ID",
        "table_name": "sales_data"
      },
      "output_alias": "sales"
    },
    {
      "step_order": 1,
      "step_type": "aggregate",
      "step_name": "Group by Region",
      "configuration": {
        "group_by": ["region"],
        "aggregations": [
          {
            "column": "quantity",
            "function": "sum",
            "alias": "total_quantity"
          },
          {
            "column": "unit_price",
            "function": "mean",
            "alias": "avg_price"
          }
        ]
      }
    },
    {
      "step_order": 2,
      "step_type": "sort",
      "step_name": "Sort by Quantity",
      "configuration": {
        "columns": ["total_quantity"],
        "ascending": [false]
      }
    }
  ]
}
```

**Note**: This has 3 steps (0, 1, 2) - make sure orders are sequential!

---

## Step 5: Execute and View Results

**Endpoint**: `POST /api/pipelines/{pipeline_id}/execute`

**Request Body**:
```json
{
  "limit": 0,
  "preview_mode": true
}
```

**Expected Response**: Aggregated data by region
```json
{
  "status": "success",
  "rows_processed": 4,
  "data": {
    "columns": ["region", "total_quantity", "avg_price"],
    "rows": [
      {"region": "North", "total_quantity": 45, "avg_price": 1250.50},
      {"region": "South", "total_quantity": 32, "avg_price": 980.25},
      ...
    ]
  }
}
```

---

## Step 6: Validate Your Pipeline

**Endpoint**: `POST /api/pipelines/{pipeline_id}/validate`

**No request body needed**

**Expected Response**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

**If validation fails**: Check that:
- Step orders are sequential (0, 1, 2, 3...)
- No duplicate step orders
- First step is always type "source"
- Configuration has all required fields

---

## Step 7: View Execution History

**Endpoint**: `GET /api/pipelines/{pipeline_id}/runs`

**Expected Response**: List of all executions
```json
[
  {
    "id": "...",
    "pipeline_id": "...",
    "status": "success",
    "started_at": "2026-01-07T10:30:00",
    "completed_at": "2026-01-07T10:30:01",
    "rows_processed": 4,
    "execution_log": {...}
  }
]
```

---

## Common Issues and Solutions

### Issue: "badly formed hexadecimal UUID string"
**Solution**: You're using a placeholder like `"YOUR_DATA_SOURCE_ID"`. Get the real UUID from `GET /api/data-sources`

### Issue: "Column not found: unit_price"
**Solution**: Check your CSV column names. They might be different (e.g., "price", "amount", "total")

### Issue: "Step order mismatch at position X"
**Solution**: Make sure step_order values are sequential: 0, 1, 2, 3... (no duplicates, no gaps)

### Issue: "No input data for filter operation"
**Solution**: First step must be type "source". Filters/aggregations need data from previous steps

### Issue: "Data source not found"
**Solution**: Verify the data_source_id exists and belongs to your user

---

## Testing Checklist

After completing all steps, you should have:

- ✅ Created 2 pipelines (filter + aggregate)
- ✅ Successfully executed both pipelines
- ✅ Viewed preview data with results
- ✅ Validated pipeline configurations
- ✅ Viewed execution history
- ✅ Understood transformation flow

---

## What's Next?

Once Phase 3 testing is complete:
1. Clean up test pipelines (use cleanup scripts if needed)
2. Commit Phase 3 code to GitHub
3. Move to Phase 4: Semantic Layer (business metrics)

---

## Quick Reference: Step Types

| Type        | Purpose                | Required Config                          |
| ----------- | ---------------------- | ---------------------------------------- |
| `source`    | Load data              | `data_source_id`, `table_name`           |
| `filter`    | Filter rows            | `conditions`, `logical_operator`         |
| `aggregate` | Group and summarize    | `group_by`, `aggregations`               |
| `select`    | Pick/rename columns    | `columns`, optional `rename`             |
| `sort`      | Order results          | `columns`, `ascending`                   |
| `join`      | Combine datasets       | `left_source`, `right_source`, join keys |
| `union`     | Stack datasets         | `sources`, `remove_duplicates`           |

---

## Filter Operators Reference

- Comparison: `==`, `!=`, `>`, `>=`, `<`, `<=`
- Lists: `in`, `not in`
- Strings: `contains`, `startswith`, `endswith`
- Nulls: `is null`, `is not null`

---

## Aggregation Functions

- `sum` - Total
- `mean` - Average
- `median` - Middle value
- `min` / `max` - Minimum/Maximum
- `count` - Count rows
- `std` / `var` - Standard deviation/Variance
