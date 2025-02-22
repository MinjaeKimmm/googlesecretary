'use client';

import * as React from 'react';
import { useState } from 'react';
import { useServiceStore } from '@/stores/service-store';
import { useSession } from 'next-auth/react';
import apiClient from '@/lib/api-client';
import { useQuery } from '@tanstack/react-query';

interface DriveFolder {
  id: string;
  name: string;
}

export function FolderSelector() {
  const { data: session } = useSession();
  const { serviceStates, updateServiceSetup } = useServiceStore();
  const driveState = serviceStates.drive;

  const { data: folders = [], isLoading } = useQuery({
    queryKey: ['drive-folders'],
    queryFn: async () => {
      const response = await apiClient.get('/api/drive/folders', {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`
        }
      });
      return response.data.folders as DriveFolder[];
    },
    enabled: !!session?.accessToken
  });

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
        <span className="text-sm text-gray-500">Loading folders...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3">
      <select
        value={driveState.selectedFolderId || 'root'}
        onChange={(e) => updateServiceSetup('drive', { selectedFolderId: e.target.value })}
        className="form-select rounded-lg border-gray-300 text-sm"
      >
        <option value="root">My Drive</option>
        {folders.map((folder) => (
          <option key={folder.id} value={folder.id}>
            {folder.name}
          </option>
        ))}
      </select>
    </div>
  );
}
