'use client';

import * as React from 'react';
import { ServiceType } from '@/types/services';
import { MessageList } from './message-list';
import { MessageInput } from './message-input';
import { useServiceStore } from '@/stores/service-store';
import VrmViewer from '../vrm/vrmViewer';

interface ChatContainerProps {
  service: ServiceType;
}

export function ChatContainer({ service }: ChatContainerProps) {
  const { serviceStates } = useServiceStore();
  const chatState = serviceStates[service].chat;

  return (
    <main className="flex-1 flex flex-col overflow-hidden container mx-auto px-4">
      <div className="flex-1 p:2 sm:p-6 justify-between flex flex-col h-80 bg-white">
        <div className="h-1/2">
          <VrmViewer />
        </div>
        <div className="flex-1 overflow-y-auto">
          <MessageList messages={chatState.messages} />
        </div>
        <div className="border-t-2 border-gray-200 px-4 pt-4 mb-2 sm:mb-0">
          <MessageInput 
            service={service}
            isLoading={chatState.isLoading}
            error={chatState.error}
          />
        </div>
      </div>
    </main>
  );
}
