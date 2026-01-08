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
