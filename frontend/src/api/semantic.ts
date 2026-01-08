import apiClient from './client';
import { SemanticCatalogResponse } from '@/types/semantic';
import { QueryRequest, QueryResponse } from '@/types/queryBuilder';

export const semanticAPI = {
  getCatalog: () =>
    apiClient.get<SemanticCatalogResponse>('/semantic/catalog').then(res => res.data),

  executeQuery: (request: QueryRequest) =>
    apiClient.post<QueryResponse>('/query-builder/execute', request).then(res => res.data),
};
