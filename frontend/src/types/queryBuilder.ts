export interface FilterCondition {
  dimension_id: string;
  operator: '=' | '!=' | '>' | '<' | '>=' | '<=' | 'IN' | 'NOT IN' | 'LIKE' | 'IS NULL' | 'IS NOT NULL';
  value?: any;
}

export interface QueryRequest {
  entity_id: string;
  dimension_ids: string[];
  measure_ids: string[];
  filters?: FilterCondition[];
  limit?: number;
}

export interface QueryResponse {
  columns: string[];
  data: Record<string, any>[];
  row_count: number;
  generated_sql: string;
  entity_name: string;
}

// Saved Query Types
export interface SavedQuery {
  id: string;
  owner_id: string;
  name: string;
  description?: string;
  entity_id: string;
  query_config: {
    dimension_ids: string[];
    measure_ids: string[];
    filters: FilterCondition[];
    limit: number;
  };
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
}

export interface SavedQueryCreate {
  name: string;
  description?: string;
  entity_id: string;
  query_config: {
    dimension_ids: string[];
    measure_ids: string[];
    filters: FilterCondition[];
    limit: number;
  };
  is_favorite?: boolean;
}

export interface SavedQueryUpdate {
  name?: string;
  description?: string;
  query_config?: {
    dimension_ids: string[];
    measure_ids: string[];
    filters: FilterCondition[];
    limit: number;
  };
  is_favorite?: boolean;
}

export interface SavedQueryListResponse {
  queries: SavedQuery[];
  total: number;
}

// Query History Types
export interface QueryHistory {
  id: string;
  owner_id: string;
  entity_id: string;
  query_config: {
    dimension_ids: string[];
    measure_ids: string[];
    filters: FilterCondition[];
    limit: number;
  };
  generated_sql: string;
  row_count: number;
  execution_time_ms: number;
  executed_at: string;
}

export interface QueryHistoryListResponse {
  history: QueryHistory[];
  total: number;
}
