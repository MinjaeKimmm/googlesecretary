'use client';

import * as React from 'react';
import { useState } from 'react';
import { ServiceType } from '@/types/services';
import { useChat } from '@/hooks/use-chat';

interface MessageInputProps {
  service: ServiceType;
  isLoading: boolean;
  error: string | null;
}

export function MessageInput({ service, isLoading, error }: MessageInputProps) {
  const [input, setInput] = useState('');
  const { sendMessage } = useChat(service);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const message = input.trim();
    setInput('');
    await sendMessage(message);
  };

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={`Ask about your ${service}...`}
        disabled={isLoading}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        disabled={isLoading || !input.trim()}
        className="rounded-lg bg-blue-500 px-4 py-2 text-white disabled:opacity-50"
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
}
