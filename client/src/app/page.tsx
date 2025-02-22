'use client';

import * as React from 'react';
import { useSession } from 'next-auth/react';
import { useServiceStore } from '@/stores/service-store';
import { ServiceType } from '@/types/services';
import { CalendarSelector } from '@/components/services/calendar/calendar-selector';
import { DriveControls } from '@/components/services/drive/drive-controls';
import { EmailControls } from '@/components/services/email/email-controls';
import { ChatContainer } from '@/components/chat/chat-container';
import SignInButton from '@/components/auth/signin-button';

export default function Home() {
  const { status } = useSession();
  const { activeService, setActiveService } = useServiceStore();

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  return (
    <main className="flex min-h-screen flex-col p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Google Workspace Assistant</h1>
        <SignInButton />
      </header>

      {status === 'authenticated' && (
        <>
          <div className="mb-8">
            <select
              value={activeService}
              onChange={(e) => setActiveService(e.target.value as ServiceType)}
              className="rounded-lg border border-gray-300 px-4 py-2"
            >
              <option value="calendar">Calendar</option>
              <option value="drive">Drive</option>
              <option value="email">Email</option>
            </select>
          </div>

          <div className="mb-8">
            {activeService === 'calendar' && <CalendarSelector />}
            {activeService === 'drive' && <DriveControls />}
            {activeService === 'email' && <EmailControls />}
          </div>

          <div className="flex-1">
            <ChatContainer service={activeService} />
          </div>
        </>
      )}
    </main>
  );
}