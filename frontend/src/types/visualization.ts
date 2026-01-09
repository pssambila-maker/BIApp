import { QueryResponse } from './queryBuilder';

export type ChartType = 'bar' | 'line' | 'area' | 'pie';

export interface ChartConfiguration {
  chart_type: ChartType;
  x_axis_column: string | null;      // For bar/line/area
  y_axis_columns: string[];          // Can be multiple for multi-series
  category_column: string | null;     // For pie chart
  value_column: string | null;       // For pie chart
}

export interface VisualizationProps {
  data: QueryResponse;
  config: ChartConfiguration;
  onConfigChange?: (config: ChartConfiguration) => void;
}
