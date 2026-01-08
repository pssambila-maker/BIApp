import { useQuery } from '@tanstack/react-query';
import { semanticAPI } from '@/api/semantic';

export function useSemanticCatalog() {
  return useQuery({
    queryKey: ['semantic-catalog'],
    queryFn: semanticAPI.getCatalog,
  });
}
