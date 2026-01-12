/**
 * Dashboard types and interfaces
 */

import { ChartConfiguration } from './visualization';

// Grid Position
export interface GridPosition {
  x: number;
  y: number;
  w: number;  // width in grid units (max 12)
  h: number;  // height in grid units
}

// Query Configuration (reuse from query builder)
export interface QueryConfig {
  entity_id: string;
  dimension_ids: string[];
  measure_ids: string[];
  filters: any[];
  limit?: number;
}

// Dashboard Widget
export interface DashboardWidget {
  id: string;
  dashboard_id: string;
  title: string;
  description?: string;
  query_config: QueryConfig;
  chart_config: ChartConfiguration;
  grid_position: GridPosition;
  position_order: number;
  refresh_interval?: number;
  created_at: string;
  updated_at: string;
}

export interface DashboardWidgetCreate {
  title: string;
  description?: string;
  query_config: QueryConfig;
  chart_config: ChartConfiguration;
  grid_position: GridPosition;
  position_order?: number;
  refresh_interval?: number;
}

export interface DashboardWidgetUpdate {
  title?: string;
  description?: string;
  query_config?: QueryConfig;
  chart_config?: ChartConfiguration;
  grid_position?: GridPosition;
  position_order?: number;
  refresh_interval?: number;
}

// Dashboard
export interface Dashboard {
  id: string;
  owner_id: string;
  name: string;
  description?: string;
  layout_config: any;
  global_filters: any[];
  is_public: boolean;
  is_favorite: boolean;
  tags: string[];
  widgets: DashboardWidget[];
  created_at: string;
  updated_at: string;
}

export interface DashboardCreate {
  name: string;
  description?: string;
  layout_config?: any;
  global_filters?: any[];
  is_public?: boolean;
  is_favorite?: boolean;
  tags?: string[];
  widgets?: DashboardWidgetCreate[];
}

export interface DashboardUpdate {
  name?: string;
  description?: string;
  layout_config?: any;
  global_filters?: any[];
  is_public?: boolean;
  is_favorite?: boolean;
  tags?: string[];
}

export interface DashboardListResponse {
  dashboards: Dashboard[];
  total: number;
}

// Widget Data
export interface WidgetDataResponse {
  widget_id: string;
  columns: string[];
  data: any[];
  row_count: number;
  generated_sql: string;
  execution_time_ms: number;
}
