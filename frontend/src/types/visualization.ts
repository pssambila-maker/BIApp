import { QueryResponse } from './queryBuilder';

export type ChartType = 'bar' | 'line' | 'area' | 'pie';

export type SortOrder = 'none' | 'ascending' | 'descending';
export type SortBy = 'category' | 'value';

export type ColorMode = 'single' | 'conditional' | 'gradient';

export interface ConditionalColorRule {
  condition: 'positive' | 'negative' | 'zero';
  color: string;
}

export interface ChartConfiguration {
  chart_type: ChartType;
  x_axis_column: string | null;      // For bar/line/area
  y_axis_columns: string[];          // Can be multiple for multi-series
  category_column: string | null;     // For pie chart
  value_column: string | null;       // For pie chart

  // Sorting configuration
  sort_order?: SortOrder;             // Sort direction
  sort_by?: SortBy;                   // Sort by category name or value

  // Color configuration
  color_mode?: ColorMode;             // How to apply colors
  single_color?: string;              // Color for single color mode
  conditional_colors?: ConditionalColorRule[];  // Rules for conditional coloring
  gradient_colors?: string[];         // Colors for gradient mode
}

export interface VisualizationProps {
  data: QueryResponse;
  config: ChartConfiguration;
  onConfigChange?: (config: ChartConfiguration) => void;
}
