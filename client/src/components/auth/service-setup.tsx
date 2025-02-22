'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { useServiceStore } from '@/stores/service-store';

interface ServiceSetupProps {
  service: 'drive' | 'email';
}

export function ServiceSetup({ service }: ServiceSetupProps) {
  const router = useRouter();
  const { data: session } = useSession();
  const { serviceStates, updateServiceSetup } = useServiceStore();
  const serviceState = serviceStates[service];

  useEffect(() => {
    if (!session) {
      router.push('/auth/signin');
    }
  }, [session, router]);

  if (!session) {
    return null;
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight">
            Setup {service.charAt(0).toUpperCase() + service.slice(1)}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Configure your {service} settings
          </p>
        </div>
        <div className="mt-8">
          {service === 'drive' && (
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700">
                Select Root Folder
              </label>
              <select
                value={serviceState.selectedFolderId}
                onChange={(e) => updateServiceSetup(service, { selectedFolderId: e.target.value })}
                className="form-select"
              >
                <option value="root">My Drive</option>
              </select>
            </div>
          )}
          {service === 'email' && (
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700">
                Select Email Folders
              </label>
              <select
                value={serviceState.selectedFolderId}
                onChange={(e) => updateServiceSetup(service, { selectedFolderId: e.target.value })}
                className="form-select"
              >
                <option value="INBOX">Inbox</option>
                <option value="SENT">Sent</option>
                <option value="DRAFT">Drafts</option>
              </select>
            </div>
          )}
          <div className="mt-6">
            <button
              onClick={() => router.push('/')}
              className="btn btn-primary w-full"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
