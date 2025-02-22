'use client';

import * as React from 'react';
import { useState } from 'react';
import { useServiceStore } from '@/stores/service-store';
import { useSession } from 'next-auth/react';

interface DriveFolder {
  id: string;
  name: string;
  hasChildren?: boolean;
}

interface BreadcrumbItem {
  id: string | null;
  name: string;
}

export function FolderSelector() {
  const { data: session } = useSession();
  const { serviceStates, updateServiceSetup } = useServiceStore();
  const driveState = serviceStates.drive;

  const [showModal, setShowModal] = useState(false);
  const [folders, setFolders] = useState<DriveFolder[]>([]);
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([
    { id: null, name: 'My Drive' }
  ]);
  const [fetchingFolders, setFetchingFolders] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFolders = async (parentId: string | null = null) => {
    console.log('Session:', { 
      hasToken: !!session?.accessToken,
      token: session?.accessToken?.substring(0, 20) + '...' // Only log part of the token
    });
    
    if (!session?.accessToken) {
      setError('Not authenticated');
      return;
    }
    
    setFetchingFolders(true);
    setError(null);
    
    try {
      const response = await fetch('/api/drive/list-folders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          parentId,
          accessToken: session.accessToken
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch folders');
      }
      
      setFolders(data.folders || []);
    } catch (err) {
      console.error('Error fetching folders:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch folders');
    } finally {
      setFetchingFolders(false);
    }
  };

  const openFolderPicker = () => {
    setShowModal(true);
    fetchFolders(null);
  };

  const navigateToFolder = (folder: DriveFolder) => {
    setCurrentFolderId(folder.id);
    setBreadcrumbs(prev => [...prev, { id: folder.id, name: folder.name }]);
    fetchFolders(folder.id);
  };

  const navigateBack = () => {
    const newBreadcrumbs = breadcrumbs.slice(0, -1);
    setBreadcrumbs(newBreadcrumbs);
    const parentId = newBreadcrumbs[newBreadcrumbs.length - 1].id;
    setCurrentFolderId(parentId);
    fetchFolders(parentId);
  };

  const handleFolderSelect = (folder: DriveFolder) => {
    const path = breadcrumbs.map(b => b.name).join('/') + '/' + folder.name;
    console.log('Selected folder path:', path);
    
    updateServiceSetup('drive', { 
      selectedFolderId: folder.id,
      selectedFolderPath: path 
    });
    setShowModal(false);
  };

  return (
    <div>
      {driveState.selectedFolderPath ? (
        <button
          onClick={openFolderPicker}
          className="group px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <span className="flex-grow text-left">
            {driveState.selectedFolderPath}
          </span>
          <span className="text-gray-400 group-hover:text-gray-600">
            →
          </span>
        </button>
      ) : (
        <button
          onClick={openFolderPicker}
          className="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
        >
          Select Folder
        </button>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded-lg max-w-lg w-full max-h-[80vh] overflow-auto">
            <div className="flex items-center space-x-2 mb-4">
              {breadcrumbs.length > 1 && (
                <button
                  onClick={navigateBack}
                  className="text-blue-500 hover:text-blue-700"
                >
                  ← Back
                </button>
              )}
              <h2 className="text-lg font-bold flex-grow">
                {breadcrumbs.map((item, index) => (
                  <span key={item.id || 'root'}>
                    {index > 0 && ' / '}
                    {item.name}
                  </span>
                ))}
              </h2>
            </div>
            
            {fetchingFolders ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-2">Loading folders...</p>
              </div>
            ) : folders.length === 0 ? (
              <p className="text-gray-500 py-4">No folders found</p>
            ) : (
              <div className="space-y-2">
                {folders.map((folder) => (
                  <div
                    key={folder.id}
                    className="w-full p-2 hover:bg-gray-100 rounded flex items-center group"
                  >
                    <button
                      onClick={() => navigateToFolder(folder)}
                      className="flex-grow flex items-center"
                    >
                      <span className="mr-2">📁</span>
                      <span className="flex-grow">{folder.name}</span>
                      <span className="text-gray-400 group-hover:text-gray-600 ml-2">→</span>
                    </button>
                    <button
                      onClick={() => handleFolderSelect(folder)}
                      className="ml-2 px-2 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Select
                    </button>
                  </div>
                ))}
              </div>
            )}

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-600">
                {error}
              </div>
            )}

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  setShowModal(false);
                  setCurrentFolderId(null);
                  setBreadcrumbs([{ id: null, name: 'My Drive' }]);
                }}
                className="bg-gray-500 hover:bg-gray-700 text-white px-4 py-2 rounded"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
