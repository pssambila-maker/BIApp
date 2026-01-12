import { QueryResponse } from '@/types/queryBuilder';
import { ChartType, ChartConfiguration, ConditionalColorRule } from '@/types/visualization';
import type { EChartsOption } from 'echarts';

/**
 * Automatically infer chart configuration from query response
 * Detects dimensions (categorical) and measures (numerical/aggregated)
 */
export function inferChartConfig(response: QueryResponse): ChartConfiguration {
  // Heuristic: Find dimensions (non-aggregated, likely categorical)
  const dimensions = response.columns.filter(col =>
    !/(sum|avg|count|min|max|total|amount|revenue|quantity|median|stddev)/i.test(col.toLowerCase())
  );

  // Find measures (aggregated or numeric columns)
  const measures = response.columns.filter(col =>
    /(sum|avg|count|min|max|total|amount|revenue|quantity|median|stddev)/i.test(col.toLowerCase()) ||
    (response.data.length > 0 && typeof response.data[0][col] === 'number')
  );

  // If we couldn't distinguish, fallback: first column as dimension, rest as measures
  const finalDimensions = dimensions.length > 0 ? dimensions : [response.columns[0]];
  const finalMeasures = measures.length > 0 ? measures : response.columns.slice(1);

  return {
    chart_type: 'bar',
    x_axis_column: finalDimensions[0] || null,
    y_axis_columns: finalMeasures.length > 0 ? finalMeasures : [],
    category_column: null,
    value_column: null,
    sort_order: 'none',
    sort_by: 'category',
    color_mode: 'conditional',
    conditional_colors: [
      { condition: 'positive', color: '#5470c6' },
      { condition: 'negative', color: '#ee6666' },
      { condition: 'zero', color: '#91cc75' },
    ],
  };
}

/**
 * Sort data based on configuration
 */
function sortData(
  data: any[],
  xColumn: string,
  yColumns: string[],
  sortOrder: string,
  sortBy: string
): any[] {
  if (sortOrder === 'none') return data;

  const sorted = [...data];
  const primaryYColumn = yColumns[0];

  sorted.sort((a, b) => {
    let compareValue = 0;

    if (sortBy === 'category') {
      // Sort by category (x-axis) alphabetically
      const aVal = String(a[xColumn] || '');
      const bVal = String(b[xColumn] || '');
      compareValue = aVal.localeCompare(bVal);
    } else {
      // Sort by value (first y-axis column)
      const aVal = Number(a[primaryYColumn] || 0);
      const bVal = Number(b[primaryYColumn] || 0);
      compareValue = aVal - bVal;
    }

    return sortOrder === 'ascending' ? compareValue : -compareValue;
  });

  return sorted;
}

/**
 * Get color for a value based on conditional rules
 */
function getConditionalColor(
  value: number,
  rules: ConditionalColorRule[] = []
): string | undefined {
  if (value > 0) {
    const rule = rules.find(r => r.condition === 'positive');
    return rule?.color;
  } else if (value < 0) {
    const rule = rules.find(r => r.condition === 'negative');
    return rule?.color;
  } else {
    const rule = rules.find(r => r.condition === 'zero');
    return rule?.color;
  }
}

/**
 * Transform QueryResponse data to ECharts option format
 */
export function transformDataForECharts(
  data: QueryResponse,
  config: ChartConfiguration,
  chartType: ChartType
): EChartsOption {
  if (chartType === 'pie') {
    return {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [{
        name: config.category_column || 'Category',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: data.data.map(row => ({
          name: String(row[config.category_column!] || ''),
          value: Number(row[config.value_column!] || 0),
        })),
      }],
    };
  }

  // Bar/Line/Area charts with sorting
  const sortedData = sortData(
    data.data,
    config.x_axis_column!,
    config.y_axis_columns,
    config.sort_order || 'none',
    config.sort_by || 'category'
  );

  const xAxisData = sortedData.map(row => String(row[config.x_axis_column!] || ''));

  // Determine if we should use conditional colors
  const useConditionalColors = config.color_mode === 'conditional' &&
                                chartType === 'bar' &&
                                config.y_axis_columns.length === 1;

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: chartType === 'bar' ? 'shadow' : 'cross'
      }
    },
    legend: {
      data: config.y_axis_columns,
      top: '5%',
      left: 'center'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLabel: {
        rotate: xAxisData.length > 10 ? 45 : 0,
        interval: 0,
        fontSize: 11
      },
      name: config.x_axis_column || '',
      nameLocation: 'middle',
      nameGap: xAxisData.length > 10 ? 50 : 30,
      nameTextStyle: {
        fontWeight: 'bold'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => {
          if (Math.abs(value) >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M';
          }
          if (Math.abs(value) >= 1000) {
            return (value / 1000).toFixed(1) + 'K';
          }
          return value.toLocaleString();
        }
      }
    },
    series: config.y_axis_columns.map(col => {
      const seriesData = sortedData.map(row => Number(row[col] || 0));

      // Apply conditional coloring if enabled
      const seriesConfig: any = {
        name: col,
        type: chartType === 'area' ? 'line' : chartType,
        data: seriesData,
        areaStyle: chartType === 'area' ? {} : undefined,
        smooth: chartType === 'line' || chartType === 'area',
        emphasis: {
          focus: 'series'
        },
      };

      // Add conditional colors for bar charts with single series
      if (useConditionalColors) {
        seriesConfig.itemStyle = {
          color: (params: any) => {
            const value = params.value;
            return getConditionalColor(value, config.conditional_colors) || '#5470c6';
          }
        };
      }

      return seriesConfig;
    }),
  };
}

/**
 * Validate chart configuration
 * Returns error message or null if valid
 */
export function validateChartConfig(
  config: ChartConfiguration,
  columns: string[]
): string | null {
  if (config.chart_type === 'pie') {
    if (!config.category_column || !config.value_column) {
      return 'Pie charts require both a category column and a value column';
    }
    if (!columns.includes(config.category_column)) {
      return `Category column "${config.category_column}" not found in results`;
    }
    if (!columns.includes(config.value_column)) {
      return `Value column "${config.value_column}" not found in results`;
    }
  } else {
    // Bar, Line, Area charts
    if (!config.x_axis_column) {
      return 'X-axis column is required';
    }
    if (!columns.includes(config.x_axis_column)) {
      return `X-axis column "${config.x_axis_column}" not found in results`;
    }
    if (config.y_axis_columns.length === 0) {
      return 'At least one Y-axis column is required';
    }
    for (const col of config.y_axis_columns) {
      if (!columns.includes(col)) {
        return `Y-axis column "${col}" not found in results`;
      }
    }
  }

  return null;
}
