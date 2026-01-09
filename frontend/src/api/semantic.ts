import apiClient from './client';
import { SemanticCatalogResponse } from '@/types/semantic';
import { QueryRequest, QueryResponse, SavedQuery, SavedQueryCreate, SavedQueryUpdate, SavedQueryListResponse, QueryHistoryListResponse } from '@/types/queryBuilder';

export const semanticAPI = {
  getCatalog: () =>
    apiClient.get<SemanticCatalogResponse>('/semantic/catalog').then(res => res.data),

  executeQuery: (request: QueryRequest) =>
    apiClient.post<QueryResponse>('/query-builder/execute', request).then(res => res.data),

  exportQuery: async (request: QueryRequest, format: 'csv' | 'xlsx' | 'json') => {
    const response = await apiClient.post(`/query-builder/export?format=${format}`, request, {
      responseType: 'blob',
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;

    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers['content-disposition'];
    let filename = `export.${format}`;
    if (contentDisposition) {
      const matches = /filename=([^;]+)/.exec(contentDisposition);
      if (matches && matches[1]) {
        filename = matches[1].replace(/['"]/g, '');
      }
    }

    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

export const savedQueryAPI = {
  create: (data: SavedQueryCreate) =>
    apiClient.post<SavedQuery>('/saved-queries', data).then(res => res.data),

  list: (favoritesOnly: boolean = false) =>
    apiClient.get<SavedQueryListResponse>(`/saved-queries?favorites_only=${favoritesOnly}`).then(res => res.data),

  get: (id: string) =>
    apiClient.get<SavedQuery>(`/saved-queries/${id}`).then(res => res.data),

  update: (id: string, data: SavedQueryUpdate) =>
    apiClient.put<SavedQuery>(`/saved-queries/${id}`, data).then(res => res.data),

  delete: (id: string) =>
    apiClient.delete(`/saved-queries/${id}`).then(res => res.data),
};

export const queryHistoryAPI = {
  list: (limit: number = 50) =>
    apiClient.get<QueryHistoryListResponse>(`/query-builder/history?limit=${limit}`).then(res => res.data),
};
