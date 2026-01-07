# Phase 3 Testing Guide - Data Transformation Engine

This guide walks you through testing the transformation pipeline functionality (Phase 3).

## Prerequisites

✅ Backend server running on http://localhost:8000
✅ PostgreSQL database with Phase 1, 2, and 3 migrations applied
✅ At least one data source created (CSV or Excel from Phase 2)
✅ Valid authentication token

---

## Part 1: Create a Simple Filter Pipeline

### Step 1: Login and Get Token

Follow steps from the main TESTING_GUIDE.md to login and get your access token.

### Step 2: Create a Filter Pipeline

This pipeline will load sales data and filter for high-value orders (>$1000).

1. Find the **POST /api/pipelines** endpoint
2. Click "Try it out"
3. Enter the following JSON (replace `data_source_id` with your CSV data source ID):

```json
{
  "name": "High Value Sales Filter",
  "description": "Filter sales data for orders over $1000",
  "is_active": true,
  "steps": [
    {
      "step_order": 0,
      "step_type": "source",
      "step_name": "Load Sales Data",
      "configuration": {
        "data_source_id": "YOUR_CSV_DATA_SOURCE_ID_HERE",
        "table_name": "sales_data"
      },
      "output_alias": "raw_sales"
    },
    {
      "step_order": 1,
      "step_type": "filter",
      "step_name": "Filter High Value Orders",
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

4. Click "Execute"
5. **Expected Result**: Status 201, pipeline created with an `id`
6. **IMPORTANT**: Copy the pipeline `id`

### Step 3: Execute the Pipeline

1. Find the **POST /api/pipelines/{pipeline_id}/execute** endpoint
2. Click "Try it out"
3. Enter your pipeline ID
4. Enter execution request body:

```json
{
  "limit": 100,
  "preview_mode": true
}
```

5. Click "Execute"
6. **Expected Result**: Status 200, filtered data showing only high-value orders
   ```json
   {
     "run_id": "...",
     "status": "success",
     "rows_processed": 5,
     "execution_time_seconds": 0.234,
     "data": {
       "columns": ["order_id", "customer_name", "product", ...],
       "rows": [
         // Only orders with unit_price > 1000
       ]
     }
   }
   ```

---

## Part 2: Create an Aggregation Pipeline

### Step 4: Create Sales by Region Pipeline

This pipeline aggregates sales data to show total sales and average price by region.

1. Find the **POST /api/pipelines** endpoint
2. Enter the following JSON:

```json
{
  "name": "Sales by Region Summary",
  "description": "Aggregate sales data by region",
  "is_active": true,
  "steps": [
    {
      "step_order": 0,
      "step_type": "source",
      "step_name": "Load Sales Data",
      "configuration": {
        "data_source_id": "YOUR_CSV_DATA_SOURCE_ID_HERE",
        "table_name": "sales_data"
      },
      "output_alias": "sales"
    },
    {
      "step_order": 1,
      "step_type": "aggregate",
      "step_name": "Summarize by Region",
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
          },
          {
            "column": "order_id",
            "function": "count",
            "alias": "order_count"
          }
        ]
      }
    },
    {
      "step_order": 2,
      "step_type": "sort",
      "step_name": "Sort by Total Quantity",
      "configuration": {
        "columns": ["total_quantity"],
        "ascending": [false]
      }
    }
  ]
}
```

3. Click "Execute"
4. Copy the pipeline ID

### Step 5: Execute the Aggregation Pipeline

1. Use **POST /api/pipelines/{pipeline_id}/execute**
2. Enter your pipeline ID
3. Execute with:

```json
{
  "limit": 100,
  "preview_mode": true
}
```

4. **Expected Result**: Aggregated data by region
   ```json
   {
     "status": "success",
     "rows_processed": 4,
     "data": {
       "columns": ["region", "total_quantity", "avg_price", "order_count"],
       "rows": [
         {
           "region": "North",
           "total_quantity": 45,
           "avg_price": 1250.50,
           "order_count": 5
         },
         ...
       ]
     }
   }
   ```

---

## Part 3: Create a Join Pipeline (If you have Employee/Projects data)

### Step 6: Create Employee-Project Join Pipeline

This pipeline joins employee data with project assignments.

1. **POST /api/pipelines** with:

```json
{
  "name": "Employee Project Assignments",
  "description": "Join employees with their projects",
  "is_active": true,
  "steps": [
    {
      "step_order": 0,
      "step_type": "source",
      "step_name": "Load Employees",
      "configuration": {
        "data_source_id": "YOUR_EXCEL_DATA_SOURCE_ID_HERE",
        "table_name": "Employees"
      },
      "output_alias": "employees"
    },
    {
      "step_order": 1,
      "step_type": "source",
      "step_name": "Load Projects",
      "configuration": {
        "data_source_id": "YOUR_EXCEL_DATA_SOURCE_ID_HERE",
        "table_name": "Projects"
      },
      "output_alias": "projects"
    },
    {
      "step_order": 2,
      "step_type": "join",
      "step_name": "Join on Employee ID",
      "configuration": {
        "left_source": "employees",
        "right_source": "projects",
        "join_type": "inner",
        "left_on": "employee_id",
        "right_on": "employee_id",
        "suffix_left": "_emp",
        "suffix_right": "_proj"
      }
    },
    {
      "step_order": 3,
      "step_type": "select",
      "step_name": "Select Relevant Columns",
      "configuration": {
        "columns": ["employee_id", "first_name", "last_name", "department", "project_name", "start_date", "end_date"]
      }
    }
  ]
}
```

2. Execute the pipeline with preview_mode=true

---

## Part 4: Pipeline Management Operations

### Step 7: List All Pipelines

1. Find **GET /api/pipelines** endpoint
2. Click "Try it out"
3. Click "Execute"
4. **Expected Result**: List of all your pipelines with step counts

### Step 8: Get Pipeline Details

1. Find **GET /api/pipelines/{pipeline_id}** endpoint
2. Enter a pipeline ID
3. Click "Execute"
4. **Expected Result**: Full pipeline details with all steps

### Step 9: Update a Pipeline

1. Find **PUT /api/pipelines/{pipeline_id}** endpoint
2. Enter a pipeline ID
3. Update with:

```json
{
  "description": "Updated description - Now includes additional filters",
  "is_active": true
}
```

4. Click "Execute"
5. **Expected Result**: Updated pipeline details

### Step 10: Add a Step to Existing Pipeline

1. Find **POST /api/pipelines/{pipeline_id}/steps** endpoint
2. Enter pipeline ID
3. Add a new step:

```json
{
  "step_order": 2,
  "step_type": "select",
  "step_name": "Select Key Columns",
  "configuration": {
    "columns": ["order_id", "product", "quantity", "region"]
  }
}
```

4. **Expected Result**: New step added

### Step 11: Validate a Pipeline

1. Find **POST /api/pipelines/{pipeline_id}/validate** endpoint
2. Enter a pipeline ID
3. Click "Execute"
4. **Expected Result**: Validation result
   ```json
   {
     "valid": true,
     "errors": [],
     "warnings": []
   }
   ```

---

## Part 5: Execution History

### Step 12: View Pipeline Runs

1. Find **GET /api/pipelines/{pipeline_id}/runs** endpoint
2. Enter a pipeline ID
3. Click "Execute"
4. **Expected Result**: List of all executions with status and timing

### Step 13: Get Specific Run Details

1. Find **GET /api/pipelines/{pipeline_id}/runs/{run_id}** endpoint
2. Enter pipeline ID and run ID from previous step
3. Click "Execute"
4. **Expected Result**: Detailed execution log showing each step's performance

---

## Part 6: Advanced Filtering Examples

### Step 14: Multi-Condition Filter

Create a pipeline with complex filtering:

```json
{
  "name": "Complex Filter Example",
  "description": "Filter with multiple conditions",
  "is_active": true,
  "steps": [
    {
      "step_order": 0,
      "step_type": "source",
      "step_name": "Load Sales",
      "configuration": {
        "data_source_id": "YOUR_DATA_SOURCE_ID",
        "table_name": "sales_data"
      }
    },
    {
      "step_order": 1,
      "step_type": "filter",
      "step_name": "Apply Multiple Filters",
      "configuration": {
        "conditions": [
          {
            "column": "region",
            "operator": "in",
            "value": ["North", "South"]
          },
          {
            "column": "quantity",
            "operator": ">=",
            "value": 2
          },
          {
            "column": "product",
            "operator": "contains",
            "value": "Laptop"
          }
        ],
        "logical_operator": "AND"
      }
    }
  ]
}
```

### Available Filter Operators:

- **Comparison**: `==`, `!=`, `>`, `>=`, `<`, `<=`
- **List**: `in`, `not in`
- **String**: `contains`, `startswith`, `endswith`
- **Null checks**: `is null`, `is not null`

---

## Part 7: Delete Operations

### Step 15: Delete a Pipeline Step

1. Find **DELETE /api/pipelines/{pipeline_id}/steps/{step_id}** endpoint
2. Enter pipeline ID and step ID
3. Click "Execute"
4. **Expected Result**: Status 204 (No Content)

### Step 16: Delete a Pipeline

1. Find **DELETE /api/pipelines/{pipeline_id}** endpoint
2. Enter a pipeline ID
3. Click "Execute"
4. **Expected Result**: Status 204 (No Content)
5. Verify deletion by listing all pipelines

---

## Expected Results Summary

After completing all steps, you should have:

✅ **Created 3+ Pipelines** - filter, aggregate, and join operations
✅ **Executed Pipelines** - with successful data transformations
✅ **Viewed Execution History** - run logs and performance metrics
✅ **Validated Pipelines** - checked configuration correctness
✅ **Updated Pipelines** - modified existing pipelines and steps
✅ **Deleted Resources** - cleaned up test data

---

## Transformation Step Types Reference

| Step Type   | Purpose                           | Required Config                                        |
| ----------- | --------------------------------- | ------------------------------------------------------ |
| `source`    | Load data from data source        | `data_source_id`, `table_name`                         |
| `filter`    | Filter rows by conditions         | `conditions`, `logical_operator`                       |
| `join`      | Join two datasets                 | `left_source`, `right_source`, `left_on`, `right_on`   |
| `aggregate` | Group and aggregate data          | `group_by`, `aggregations`                             |
| `select`    | Select/rename columns             | `columns`, optional `rename`                           |
| `sort`      | Sort by columns                   | `columns`, `ascending`                                 |
| `union`     | Combine multiple datasets         | `sources`, `remove_duplicates`                         |

---

## Aggregation Functions Reference

- `sum` - Sum of values
- `mean` - Average value
- `median` - Median value
- `min` - Minimum value
- `max` - Maximum value
- `count` - Count of rows
- `std` - Standard deviation
- `var` - Variance

---

## Troubleshooting

### Issue: Pipeline execution fails with "No input data"
**Solution**: Ensure steps after the first have input from previous steps. The first step must be a `source` type.

### Issue: Column not found error
**Solution**: Check that column names match exactly (case-sensitive). Use schema endpoint to verify available columns.

### Issue: Join fails with key error
**Solution**: Verify that join columns exist in both datasets and contain matching values.

### Issue: Aggregation produces empty result
**Solution**: Check that group_by columns exist and aggregation functions are valid.

### Issue: "Pipeline not found"
**Solution**: Verify you're using the correct pipeline ID and are authenticated as the pipeline owner.

---

## Performance Tips

1. **Use aliases**: Name intermediate results with `output_alias` for easier reference in joins
2. **Filter early**: Apply filters as early as possible to reduce data volume
3. **Select columns**: Use select steps to keep only needed columns
4. **Preview mode**: Always test with `preview_mode: true` first
5. **Limit rows**: Use the `limit` parameter during testing

---

## Next Steps

Once all tests pass, you're ready for:
- **Phase 4**: Semantic Layer (business metrics and calculations)
- **Phase 5**: Analytics Canvas (drag-and-drop visualization builder)
- **Phase 6**: Dashboard Builder (interactive dashboards)
