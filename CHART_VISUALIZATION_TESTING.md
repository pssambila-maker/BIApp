# Chart Visualization Testing Guide

## Phase 8a: MVP Charts - Testing Checklist

**Testing Date**: 2026-01-08
**Servers Running**:
- Frontend: http://localhost:3000
- Backend: http://0.0.0.0:8000

---

## Test Environment

1. ✅ Frontend dev server running at http://localhost:3000
2. ✅ Backend API server running at http://0.0.0.0:8000
3. ✅ Database connected and migrations applied
4. ✅ Apache ECharts library installed (v5.6.0)
5. ✅ echarts-for-react wrapper installed (v3.0.3)

---

## Component Verification

### Files Created
- [x] `frontend/src/types/visualization.ts` - Type definitions
- [x] `frontend/src/features/query-builder/utils/chartUtils.ts` - Chart utilities
- [x] `frontend/src/features/query-builder/components/ChartTypeSelector.tsx` - Chart type selector
- [x] `frontend/src/features/query-builder/components/AxisConfigPanel.tsx` - Axis configuration
- [x] `frontend/src/features/query-builder/components/ChartVisualization.tsx` - Main chart component
- [x] `frontend/src/features/query-builder/QueryBuilder.tsx` - Integration

### Files Modified
- [x] `frontend/package.json` - Dependencies added
- [x] `backend/app/api/saved_queries.py` - Fixed import path

---

## Test Scenarios

### 1. Basic Chart Display

#### Test 1.1: Execute Query and View Bar Chart
**Steps**:
1. Navigate to http://localhost:3000
2. Log in with test credentials
3. Go to Query Builder page
4. Select an entity (e.g., "Sales")
5. Add at least 1 dimension (e.g., "product_category")
6. Add at least 1 measure (e.g., "total_revenue")
7. Click "Run Query"
8. Verify table displays with results
9. Click the "Chart" tab (with BarChart icon)

**Expected Results**:
- Chart view displays with automatic configuration
- Bar chart renders with data
- X-axis shows dimension values
- Y-axis shows measure values
- Chart has proper labels and legend
- Chart is responsive (500px height)

#### Test 1.2: Switch Between Table and Chart Views
**Steps**:
1. After executing a query
2. Click "Chart" tab → view chart
3. Click "Table" tab → view table
4. Repeat toggle 3-4 times

**Expected Results**:
- Smooth transition between views
- No data loss
- No console errors
- Export button remains visible in both views

---

### 2. Chart Type Switching

#### Test 2.1: Bar Chart
**Steps**:
1. Execute query with 1 dimension + 2 measures
2. Switch to Chart view
3. Select "Bar" chart type

**Expected Results**:
- Vertical bars grouped by dimension
- Multiple series for multiple measures
- Legend shows measure names
- Tooltip shows values on hover
- Proper formatting (K/M suffixes for large numbers)

#### Test 2.2: Line Chart
**Steps**:
1. From bar chart, click "Line" button
2. Observe chart transition

**Expected Results**:
- Smooth transition to line chart
- Lines connect data points
- Markers visible on data points
- Same data as bar chart
- Area under line is not filled

#### Test 2.3: Area Chart
**Steps**:
1. From line chart, click "Area" button
2. Observe chart transition

**Expected Results**:
- Smooth transition to area chart
- Area under line is filled with color
- Semi-transparent fill
- Same data as line chart

#### Test 2.4: Pie Chart
**Steps**:
1. From area chart, click "Pie" button
2. Observe UI change

**Expected Results**:
- Axis config changes to "Category Column" and "Value Column"
- Alert message: "Pie charts require exactly one category column and one value column"
- Auto-selects first dimension as category, first measure as value
- Pie chart renders with slices
- Legend shows category values
- Tooltip shows percentage and value

---

### 3. Axis Configuration

#### Test 3.1: Change X-Axis (Bar/Line/Area)
**Steps**:
1. Execute query with 2+ dimensions and 2+ measures
2. View bar chart
3. In Axis Config Panel, change X-Axis dropdown
4. Select different dimension

**Expected Results**:
- Chart updates immediately
- New dimension appears on X-axis
- Data re-aggregates correctly
- No errors

#### Test 3.2: Change Y-Axis (Single Measure)
**Steps**:
1. View bar chart with multiple measures selected
2. Clear Y-Axis selection
3. Select only 1 measure

**Expected Results**:
- Chart shows single series
- Legend shows only selected measure
- Chart remains valid

#### Test 3.3: Change Y-Axis (Multiple Measures)
**Steps**:
1. View bar chart with 1 measure
2. Add 2 more measures to Y-Axis
3. Observe chart update

**Expected Results**:
- Chart shows 3 series (grouped bars)
- Legend shows all 3 measures
- Colors differentiate series
- All measures visible

#### Test 3.4: Change Pie Chart Category/Value
**Steps**:
1. View pie chart
2. Change Category Column dropdown
3. Change Value Column dropdown

**Expected Results**:
- Pie chart updates immediately
- Slices reflect new category
- Values reflect new measure
- Percentages recalculated

---

### 4. Auto-Configuration Intelligence

#### Test 4.1: Dimension/Measure Detection
**Steps**:
1. Execute query with columns:
   - `product_name` (dimension)
   - `order_date` (dimension)
   - `sum_total_revenue` (measure)
   - `avg_quantity` (measure)
2. Switch to Chart view

**Expected Results**:
- Auto-detects `product_name` as X-axis (first non-aggregated column)
- Auto-detects `sum_total_revenue` and `avg_quantity` as Y-axis (aggregation keywords)
- Chart displays correctly without manual config

#### Test 4.2: All Numeric Columns
**Steps**:
1. Execute query returning only numeric columns (e.g., year, sum_revenue, avg_price)
2. Switch to Chart view

**Expected Results**:
- First column becomes X-axis
- Remaining columns become Y-axis
- Chart still renders correctly
- Fallback logic works

---

### 5. Validation and Error Handling

#### Test 5.1: Invalid Bar Chart Config (No Y-Axis)
**Steps**:
1. View bar chart
2. Clear all Y-Axis selections

**Expected Results**:
- Chart disappears
- Error Alert displays: "Bar charts require at least one Y-axis column"
- Error type: "error" with icon
- Can recover by selecting Y-axis column

#### Test 5.2: Invalid Pie Chart Config (No Category)
**Steps**:
1. View pie chart
2. Clear Category Column selection

**Expected Results**:
- Chart disappears
- Error Alert displays: "Pie charts require both category and value columns"
- Can recover by selecting category

#### Test 5.3: Invalid Pie Chart Config (No Value)
**Steps**:
1. View pie chart
2. Clear Value Column selection

**Expected Results**:
- Chart disappears
- Error Alert displays validation error
- Can recover by selecting value column

---

### 6. Edge Cases

#### Test 6.1: Empty Results
**Steps**:
1. Execute query with filters that return 0 rows
2. Switch to Chart view

**Expected Results**:
- Chart component handles gracefully
- Either shows empty state or error message
- No JavaScript errors in console

#### Test 6.2: Single Data Point
**Steps**:
1. Execute query returning exactly 1 row
2. View each chart type

**Expected Results**:
- Bar chart: Shows 1 bar
- Line chart: Shows 1 point (no line)
- Area chart: Shows 1 point
- Pie chart: Shows 1 full slice (100%)

#### Test 6.3: Large Dataset (100+ rows)
**Steps**:
1. Execute query returning 100+ rows
2. View bar chart

**Expected Results**:
- Chart renders without lag
- X-axis labels rotate if needed for readability
- Zoom/scroll functionality available (if implemented)
- No performance issues

#### Test 6.4: Very Large Numbers
**Steps**:
1. Execute query with values > 1,000,000
2. View chart

**Expected Results**:
- Numbers formatted with K/M suffixes (e.g., "1.5M", "250K")
- Tooltip shows full precision
- Readable axis labels

#### Test 6.5: NULL Values
**Steps**:
1. Execute query that may contain NULL values
2. View chart

**Expected Results**:
- NULL values handled gracefully
- Either excluded from chart or shown as 0
- No errors
- Tooltip indicates NULL if applicable

#### Test 6.6: Long Category Names
**Steps**:
1. Execute query with long text dimension values
2. View bar chart

**Expected Results**:
- X-axis labels rotate or truncate
- Full value visible in tooltip
- Chart remains readable

---

### 7. Integration Tests

#### Test 7.1: Save Query → Load Query → View Chart
**Steps**:
1. Execute query and configure chart
2. Save the query
3. Clear/reset
4. Load saved query
5. Switch to Chart view

**Expected Results**:
- Query executes correctly
- Chart auto-configures based on columns
- Chart displays same data as before

#### Test 7.2: Query History → View Chart
**Steps**:
1. Execute multiple queries
2. View query history
3. Reload previous query
4. Switch to Chart view

**Expected Results**:
- Previous query results load
- Chart configures correctly
- All chart types work

#### Test 7.3: Export with Chart View Active
**Steps**:
1. Execute query
2. Switch to Chart view
3. Click Export dropdown
4. Export as CSV/JSON

**Expected Results**:
- Export still works (exports table data)
- No impact on chart display
- Files download correctly

#### Test 7.4: Clear Query from Chart View
**Steps**:
1. Execute query and view chart
2. Click "Clear" button

**Expected Results**:
- Chart view disappears
- View mode resets to "table"
- Chart config is cleared
- Form resets to initial state

---

### 8. UI/UX Tests

#### Test 8.1: Responsive Layout
**Steps**:
1. View chart
2. Resize browser window (smaller/larger)

**Expected Results**:
- Chart resizes responsively
- Maintains aspect ratio
- No overflow issues
- Controls remain accessible

#### Test 8.2: Tab Toggle Icons
**Steps**:
1. Observe Table/Chart toggle (Segmented control)

**Expected Results**:
- TableOutlined icon visible for Table tab
- BarChartOutlined icon visible for Chart tab
- Active tab highlighted
- Clear visual feedback on click

#### Test 8.3: Chart Type Selector Icons
**Steps**:
1. View chart type selector buttons

**Expected Results**:
- BarChartOutlined icon for Bar
- LineChartOutlined icon for Line
- AreaChartOutlined icon for Area
- PieChartOutlined icon for Pie
- Icons clearly distinguishable
- Active type highlighted

#### Test 8.4: Loading States
**Steps**:
1. Execute long-running query
2. Observe chart view during execution

**Expected Results**:
- Loading indicator shown (if implemented)
- No chart rendered until data arrives
- Smooth transition when data loads

---

## Browser Console Checks

For each test, verify:
- [ ] No JavaScript errors
- [ ] No React warnings
- [ ] No 404 network requests
- [ ] ECharts library loads correctly
- [ ] No memory leaks (check via Dev Tools Performance tab)

---

## Performance Benchmarks

| Test Scenario | Expected Performance |
|---------------|---------------------|
| Query execution (10 rows) | < 500ms |
| Chart render (10 rows) | < 200ms |
| Chart type switch | < 100ms |
| Axis config change | < 100ms |
| Table ↔ Chart toggle | < 50ms |
| Query execution (100 rows) | < 1000ms |
| Chart render (100 rows) | < 500ms |

---

## Known Limitations (Phase 8a MVP)

1. **No Persistence**: Chart configurations are not saved with queries (Phase 8b feature)
2. **No Advanced Chart Types**: Only Bar, Line, Area, Pie (more in future phases)
3. **No Chart Customization**: Colors, fonts, themes are default (future enhancement)
4. **No Drill-Down**: No interactive filtering from chart clicks (future feature)
5. **No Multi-Chart Dashboards**: Only single chart view (Phase 8b feature)

---

## Testing Results Summary

**Date Tested**: _________
**Tested By**: _________
**Browser**: _________
**OS**: _________

### Results
- [ ] All basic chart display tests passed
- [ ] All chart type switching tests passed
- [ ] All axis configuration tests passed
- [ ] Auto-configuration works correctly
- [ ] Validation and error handling works
- [ ] Edge cases handled gracefully
- [ ] Integration tests passed
- [ ] UI/UX meets expectations
- [ ] No console errors
- [ ] Performance acceptable

### Issues Found
_List any bugs, issues, or unexpected behavior:_

1.
2.
3.

### Overall Status
- [ ] ✅ **PASS** - Ready for production
- [ ] ⚠️ **PASS WITH MINOR ISSUES** - Can deploy with known limitations
- [ ] ❌ **FAIL** - Requires fixes before deployment

---

## Next Steps (Post-Testing)

If all tests pass:
1. Mark Phase 8a as COMPLETE
2. Update README with Phase 8a completion
3. Consider Phase 8b (Dashboard Builder with persistence)
4. Or proceed with Phase 9 based on roadmap

If issues found:
1. Document all bugs
2. Prioritize critical vs. nice-to-have fixes
3. Fix critical issues
4. Re-test
5. Mark as complete once stable
