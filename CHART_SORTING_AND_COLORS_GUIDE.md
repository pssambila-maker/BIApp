# Chart Sorting and Conditional Colors Guide

This guide explains how to use the new sorting and conditional coloring features in the Query Builder chart visualizations.

## Quick Access

- **Query Builder**: [http://localhost:3000/query-builder](http://localhost:3000/query-builder)

## Features Overview

### 1. Chart Sorting

Sort your chart data in ascending or descending order, either by category (X-axis) or by value (Y-axis).

#### How to Sort Data

1. Execute a query with dimensions and measures
2. Switch to **Chart** view
3. In the **Chart Configuration** panel, find the **Sorting** section
4. Select **Sort Order**:
   - **No Sorting**: Display data in the order returned by the query
   - **Ascending**: Sort from lowest to highest (A → Z, 1 → 9)
   - **Descending**: Sort from highest to lowest (Z → A, 9 → 1)
5. Select **Sort By**:
   - **Sort by Category (X-axis)**: Alphabetical sorting by category names
   - **Sort by Value (Y-axis)**: Numerical sorting by the first measure value

#### Example Use Cases

**Example 1: Top 10 Products by Sales**
- Sort Order: Descending
- Sort By: Value
- Result: Highest selling products appear first

**Example 2: Alphabetical Category List**
- Sort Order: Ascending
- Sort By: Category
- Result: Categories displayed A-Z

### 2. Conditional Colors

Apply different colors to bars based on whether values are positive, negative, or zero - just like Tableau Desktop!

#### How Conditional Colors Work

Conditional coloring automatically applies different colors to bars based on the value:
- **Positive values** (> 0): Blue by default
- **Negative values** (< 0): Red by default
- **Zero values** (= 0): Green by default

#### How to Configure Colors

1. Execute a query with **one measure** (conditional colors only work with single measures)
2. Switch to **Chart** view and select **Bar chart** type
3. In the **Chart Configuration** panel, find the **Colors** section
4. **Color Mode** should be set to **Conditional (by value)**
5. Click on each color picker to customize:
   - **Positive values**: Choose color for positive numbers
   - **Negative values**: Choose color for negative numbers
   - **Zero values**: Choose color for zero

#### Requirements for Conditional Colors

Conditional coloring is available when:
- ✅ Chart type is **Bar**
- ✅ Only **one measure** is selected
- ✅ Color mode is set to **Conditional (by value)**

Conditional coloring is NOT available when:
- ❌ Chart type is Line, Area, or Pie
- ❌ Multiple measures are selected
- ❌ Color mode is set to Single color

## Practical Example: Profit Analysis by Sub-Category

Let's analyze profit by product sub-category to identify which categories are profitable (positive) and which are losing money (negative).

### Step 1: Build the Query

1. Navigate to **Query Builder**
2. Select Entity: **Superstore**
3. Select Dimension: **Sub-Category**
4. Select Measure: **Total Profit (SUM)**
5. Click **Execute Query**

### Step 2: Configure Chart

1. Switch to **Chart** view
2. Chart Type: **Bar** (already selected)
3. X-axis: sub_category
4. Y-axis: total_profit

### Step 3: Apply Sorting

1. In **Sorting** section:
   - Sort Order: **Descending**
   - Sort By: **Value (Y-axis)**
2. Result: Most profitable categories appear first, least profitable (negative) at the end

### Step 4: Apply Conditional Colors

1. In **Colors** section:
   - Color Mode: **Conditional (by value)** (already set)
2. The chart will now show:
   - **Blue bars** for profitable sub-categories (positive profit)
   - **Red bars** for unprofitable sub-categories (negative profit)
   - **Green bars** if any sub-category has exactly zero profit

### Step 5: Customize Colors (Optional)

Want to use different colors? Click the color pickers:
- Positive values: Change from blue to green (#52c41a)
- Negative values: Change from red to dark red (#cf1322)
- Zero values: Keep as is or customize

### Expected Result

You should see a bar chart with:
- Sub-categories sorted from most profitable to least profitable
- Profitable categories (like Copiers, Phones, Accessories) in blue/green
- Unprofitable categories (like Tables, Bookcases) in red
- Clear visual distinction between profit and loss

## Tips and Best Practices

### Sorting Tips

1. **Sort by Value for Rankings**: When you want to see top/bottom performers
2. **Sort by Category for A-Z Lists**: When you want alphabetical organization
3. **No Sorting for Time Series**: Keep chronological order for date-based data

### Color Tips

1. **Use Standard Colors**: Red for negative/bad, Green for positive/good
2. **Consider Color Blindness**: Test your colors with color-blind friendly palettes
3. **Limit Color Variety**: Too many colors can be confusing
4. **Match Your Brand**: Use your organization's brand colors

### Performance Tips

1. Sorting happens in the browser, so it's fast even with large datasets
2. The LIMIT (default 1000 rows) still applies before sorting
3. For very large datasets, consider using database-level sorting via filters

## Technical Details

### Default Colors

The default conditional color scheme is:
- Positive: `#5470c6` (ECharts default blue)
- Negative: `#ee6666` (ECharts red)
- Zero: `#91cc75` (ECharts green)

### Sorting Algorithm

- **Category sorting**: Uses JavaScript's `localeCompare()` for proper string comparison
- **Value sorting**: Numerical comparison of the first Y-axis measure
- **Stability**: Sort is stable, meaning equal values maintain their original order

### Color Application

Colors are applied at render time using ECharts' `itemStyle.color` function:
```javascript
itemStyle: {
  color: (params) => {
    if (value > 0) return positiveColor;
    if (value < 0) return negativeColor;
    return zeroColor;
  }
}
```

## Limitations

1. **Conditional colors** only work for bar charts with a single measure
2. **Sorting** applies to all series in multi-series charts (sorts by first Y-axis column)
3. **Pie charts** don't support sorting or conditional colors
4. **Line/Area charts** don't support conditional colors (they use series colors)

## Troubleshooting

### Colors Not Changing

**Issue**: Bars remain the same color despite changing color mode

**Solutions**:
1. Verify chart type is **Bar**
2. Ensure only **one measure** is selected
3. Check that color mode is set to **Conditional**
4. Try selecting a different measure and switching back

### Sorting Not Working

**Issue**: Data appears unsorted despite changing sort order

**Solutions**:
1. Verify sort order is not set to **"No Sorting"**
2. Check that you have data in the results
3. Try switching between ascending/descending
4. Refresh the query and try again

### UI Not Showing Sorting/Colors Panels

**Issue**: Sorting and Colors sections don't appear

**Solutions**:
1. Ensure you're in **Chart** view (not Table view)
2. For sorting/colors: Switch from Pie chart to Bar/Line/Area
3. Refresh the page
4. Check browser console for errors

## Related Documentation

- **[Semantic Catalog Guide](SEMANTIC_CATALOG_GUIDE.md)** - Creating entities and measures
- **[Chart Visualization Testing](CHART_VISUALIZATION_TESTING.md)** - Testing chart features
- **[Query Builder Usage](SEMANTIC_CATALOG_GUIDE.md#query-builder-usage)** - Building queries

## Summary

With sorting and conditional colors, you can:
- ✅ Sort charts by category name or measure value
- ✅ Sort in ascending or descending order
- ✅ Apply colors based on positive/negative/zero values
- ✅ Customize colors with a color picker
- ✅ Create Tableau-style profit/loss visualizations
- ✅ Quickly identify trends and outliers

These features bring your BI platform closer to the functionality of professional tools like Tableau Desktop!
