'use client';

import * as React from 'react';
import { ServiceType } from '@/types/services';
import { MessageList } from './message-list';
import { MessageInput } from './message-input';
import { useServiceStore } from '@/stores/service-store';

interface ChatContainerProps {
  service: ServiceType;
}

export function ChatContainer({ service }: ChatContainerProps) {
  const { serviceStates } = useServiceStore();
  const chatState = serviceStates[service].chat;

  return (
    <div className="flex flex-col h-[600px] border border-gray-200 rounded-lg bg-white">
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={chatState.messages} />
      </div>
      <div className="border-t border-gray-200 p-4">
        <MessageInput 
          service={service}
          isLoading={chatState.isLoading}
          error={chatState.error}
        />
      </div>
    </div>
  );
}
