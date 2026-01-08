import apiClient from './client';
import {
  DataSource,
  DataSourceCreate,
  DataSourceUpdate,
  DataSourceTable,
} from '@/types/dataSource';

export const dataSourceAPI = {
  // Get all data sources
  getAll: (skip = 0, limit = 100) =>
    apiClient
      .get<DataSource[]>('/data-sources/', { params: { skip, limit } })
      .then(res => res.data),

  // Get a single data source by ID
  getById: (id: string) =>
    apiClient.get<DataSource>(`/data-sources/${id}`).then(res => res.data),

  // Create a new data source
  create: (data: DataSourceCreate) =>
    apiClient.post<DataSource>('/data-sources/', data).then(res => res.data),

  // Update a data source
  update: (id: string, data: DataSourceUpdate) =>
    apiClient.put<DataSource>(`/data-sources/${id}`, data).then(res => res.data),

  // Delete a data source
  delete: (id: string) =>
    apiClient.delete(`/data-sources/${id}`).then(res => res.data),

  // Test connection
  testConnection: (id: string) =>
    apiClient.post<{ status: string; message: string }>(`/data-sources/${id}/test`).then(res => res.data),

  // Sync/scan tables
  sync: (id: string) =>
    apiClient.post<{ tables_found: number }>(`/data-sources/${id}/sync`).then(res => res.data),

  // Get tables for a data source
  getTables: (id: string) =>
    apiClient.get<DataSourceTable[]>(`/data-sources/${id}/tables`).then(res => res.data),
};
