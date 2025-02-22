'use client';

import * as React from 'react';
import { ServiceType } from '@/types/services';
import { useChat } from '@/hooks/use-chat';

interface MessageInputProps {
  service: ServiceType;
  isLoading: boolean;
  isRecording: boolean;
  startRecording: () => void;
  input: string;  // ✅ input 상태 추가
  setInput: (value: string) => void;  // ✅ input 상태 변경 함수 추가
  error: string | null;
}

export function MessageInput({ service, isLoading, isRecording, startRecording, input, setInput, error }: MessageInputProps) {
  const { sendMessage } = useChat(service);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const message = input.trim();
    setInput(''); // ✅ 메시지 전송 후 input 초기화
    await sendMessage(message);
  };

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      {/* 🎤 마이크 버튼 */}
      <button
        type="button"
        onClick={startRecording} // 🎤 버튼 클릭 시 음성 인식 시작
        disabled={isRecording || isLoading}
        className={`rounded-lg px-4 py-2 text-white disabled:opacity-50 bg-blue-500`}
      >
        {isRecording ? <img src="/loading.png" className="h-6 w-auto" /> : <img src="/mic.png" className="h-6 w-auto"/>}
      </button>

      {/* 텍스트 입력 */}
      <input
        type="text"
        value={input} // ✅ input 값 바인딩
        onChange={(e) => setInput(e.target.value)} // ✅ 사용자 입력 반영
        placeholder={`Ask about your ${service}...`}
        disabled={isLoading}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* 전송 버튼 */}
      <button
        type="submit"
        disabled={isLoading || !input.trim()}
        className="rounded-lg bg-blue-500 px-4 py-2 text-white disabled:opacity-50"
      >
        {isLoading ?
          <img src="/loading.png" className=""/> 
          : <img src="/send.png" className='w-8 h-auto'/>}
      </button>
    </form>
  );
}
