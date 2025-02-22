'use client';

import * as React from 'react';
import { useSession } from 'next-auth/react';
import { useServiceStore } from '@/stores/service-store';
import { ServiceType } from '@/types/services';
import { CalendarSelector } from '@/components/services/calendar/calendar-selector';
import { DriveControls } from '@/components/services/drive/drive-controls';
import { EmailControls } from '@/components/services/email/email-controls';
import { ChatContainer } from '@/components/chat/chat-container';
import LogoutDropdown from '@/components/logOutDropDown';
import SignInButton from '@/components/auth/signin-button';

export default function Home() {
  const { status, data: session } = useSession();
  const { activeService, setActiveService } = useServiceStore();
  const [language, setLanguage] = React.useState("eb-US");

  // 언어 변경 함수
  const toggleLanguage = () => {
    setLanguage((prev) => (prev === "ko-KR" ? "en-US" : "ko-KR"));
  };

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  return (
    <main className="flex min-h-screen flex-col p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Google Workspace Assistant</h1>

        <div className="flex space-x-4">
          {/* ✅ 언어 변경 버튼 */}
          <button
            onClick={toggleLanguage}
            className={`px-4 py-2 rounded-lg bg-gray-200`}
          >
            {language === "ko-KR" ? "KR" : "EN"}
          </button>

          {/* ✅ 로그인 사용자에게 LogoutDropdown 표시 */}
          {status === "authenticated" && session?.user && (
            <LogoutDropdown user={session.user} />
          )}
          <SignInButton />
        </div>
      </header>

      {status === 'authenticated' && (
        <>
          <div className="flex items-center space-x-4">
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
          </div>

          <div className="flex-1">
            <ChatContainer service={activeService} language={language} />
          </div>
        </>
      )}
    </main>
  );
}
