'use client';

import * as React from 'react';
import { ServiceType } from '@/types/services';
import { useServiceStatus } from '@/hooks/use-service-status';
import { useMutation } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import apiClient from '@/lib/api-client';

interface ServiceStatusProps {
  service: Extract<ServiceType, 'drive' | 'email' | 'calendar'>;
}

export function ServiceStatus({ service }: ServiceStatusProps) {
  const { data: session } = useSession();
  const { data: userData, isLoading, refetch } = useServiceStatus(service);
  const serviceStatus = userData?.services[service];

  const setupMutation = useMutation({
    mutationFn: async () => {
      if (!session?.accessToken) {
        throw new Error('No access token available');
      }
      const response = await apiClient.post(`/api/auth/${service}/setup`, {
        credential: session.accessToken,
        folderId: service === 'drive' ? 'root' : undefined
      }, {
        headers: {
          Authorization: `Bearer ${session.accessToken}`
        }
      });
      return response.data;
    },
    onSuccess: () => {
      refetch();
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
        <span className="text-sm text-gray-500">Loading status...</span>
      </div>
    );
  }

  if (setupMutation.isPending) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
        <span className="text-sm text-gray-500">Setting up {service}...</span>
      </div>
    );
  }

  if (!serviceStatus?.is_setup) {
    return (
      <button
        onClick={() => setupMutation.mutate()}
        className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium"
      >
        Setup {service.charAt(0).toUpperCase() + service.slice(1)}
      </button>
    );
  }

  return (
    <div className="flex items-center space-x-3">
      <span className="text-sm text-green-600 font-medium flex items-center">
        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
        Connected
      </span>
      <button
        onClick={() => setupMutation.mutate()}
        className="text-gray-600 hover:text-gray-800 text-sm underline"
      >
        Update
      </button>
    </div>
  );
}
