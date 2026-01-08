export interface SemanticDimension {
  id: string;
  name: string;
  description: string | null;
  sql_column: string;
  data_type: 'string' | 'integer' | 'date' | 'boolean' | 'decimal';
  display_format: string | null;
  is_hidden: boolean;
  display_order: number;
  semantic_entity_id: string;
  created_at: string;
  updated_at: string;
}

export interface SemanticMeasure {
  id: string;
  name: string;
  description: string | null;
  calculation_type: string;
  aggregation_function: 'SUM' | 'COUNT' | 'AVG' | 'MIN' | 'MAX' | 'MEDIAN' | 'STDDEV';
  base_column: string;
  format: 'currency' | 'percent' | 'integer' | 'decimal' | null;
  default_format_pattern: string | null;
  is_hidden: boolean;
  semantic_entity_id: string;
  created_at: string;
  updated_at: string;
}

export interface SemanticEntity {
  id: string;
  name: string;
  plural_name: string | null;
  description: string | null;
  primary_table: string;
  is_certified: boolean;
  tags: string[];
  dimensions: SemanticDimension[];
  measures: SemanticMeasure[];
}

export interface SemanticCatalogResponse {
  entities: SemanticEntity[];
  total_entities: number;
  total_dimensions: number;
  total_measures: number;
}
