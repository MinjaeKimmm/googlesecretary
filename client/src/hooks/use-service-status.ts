import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { ServiceType, UserData } from '@/types/services';
import apiClient from '@/lib/api-client';

export function useServiceStatus(service: ServiceType) {
  type QueryResult = UserData;
  const { data: session } = useSession();

  return useQuery({
    queryKey: ['service-status', service],
    queryFn: async () => {
      if (!session?.accessToken) {
        throw new Error('No access token');
      }

      const response = await apiClient.get('/api/auth/user/data', {
        headers: {
          Authorization: `Bearer ${session.accessToken}`
        }
      });

      return response.data;
    },
    enabled: !!session?.accessToken,
    staleTime: 30000, // Consider data fresh for 30 seconds
    refetchOnWindowFocus: false
  });
}
