export type DataSourceType = 'postgresql' | 'mysql' | 'csv' | 'excel';

export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  schema?: string;
  ssl_enabled?: boolean;
}

export interface FileConfig {
  file_path: string;
  sheet_name?: string;
  delimiter?: string;
  encoding?: string;
}

export interface DataSource {
  id: string;
  name: string;
  description: string | null;
  type: DataSourceType;
  is_certified: boolean;
  schema_metadata: Record<string, any> | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface DataSourceCreate {
  name: string;
  description?: string;
  type: DataSourceType;
  connection_config: DatabaseConfig | FileConfig;
}

export interface DataSourceUpdate {
  name?: string;
  description?: string;
  connection_config?: DatabaseConfig | FileConfig;
  is_certified?: boolean;
}

export interface DataSourceTable {
  id: string;
  data_source_id: string;
  schema_name: string | null;
  table_name: string;
  row_count: number | null;
  column_count: number | null;
  last_scanned_at: string | null;
  created_at: string;
  updated_at: string;
}
