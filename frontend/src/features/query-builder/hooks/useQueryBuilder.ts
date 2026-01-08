import { useMutation } from '@tanstack/react-query';
import { semanticAPI } from '@/api/semantic';
import { QueryRequest } from '@/types/queryBuilder';

export const useExecuteQuery = () => {
  return useMutation({
    mutationFn: (request: QueryRequest) => semanticAPI.executeQuery(request),
  });
};
