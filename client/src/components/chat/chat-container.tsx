'use client';

import * as React from 'react';
import { useState, useEffect } from 'react';
import { ServiceType } from '@/types/services';
import { MessageList } from './message-list';
import { MessageInput } from './message-input';
import { useServiceStore } from '@/stores/service-store';
import VrmViewer from '../vrm/vrmViewer';

interface ChatContainerProps {
  service: ServiceType;
  language: string; // ✅ 추가: 선택된 언어 prop
}

export function ChatContainer({ service, language }: ChatContainerProps) {
  const { serviceStates } = useServiceStore();
  const chatState = serviceStates[service].chat;
  const [isRecording, setIsRecording] = useState(false);
  const [speechRecognition, setSpeechRecognition] = useState<SpeechRecognition | null>(null);
  const [input, setInput] = useState(""); 
  const [selectedCharacter, setSelectedCharacter] = useState("bunny");

  // 🎤 음성 인식 초기화 (언어 변경 시 재설정)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognitionAPI =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognitionAPI) {
        const recognition = new SpeechRecognitionAPI();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = language; // ✅ 선택된 언어 반영
        setSpeechRecognition(recognition);
      }
    }
  }, [language]); // ✅ 언어가 변경될 때마다 실행

  // 🎤 음성 녹음 시작 함수
  const startRecording = () => {
    if (!speechRecognition) return;

    setIsRecording(true);
    speechRecognition.start();

    speechRecognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript; // 인식된 텍스트
      console.log(`🎙️ [${language}] 음성 인식 결과:`, transcript);
      setInput(transcript); // ✅ 음성 인식 결과를 input 상태에 반영
    };

    speechRecognition.onend = () => {
      setIsRecording(false);
    };

    speechRecognition.onerror = (event) => {
      console.error("Speech recognition error:", event);
      setIsRecording(false);
    };
  };

  return (
    <main className="flex-1 flex flex-col overflow-hidden container mx-auto px-4">
      <div className="flex-1 p:2 sm:p-6 justify-between flex flex-col h-80 bg-white">
        <div className="h-1/2">
          <VrmViewer selectedCharacter={selectedCharacter}/>
        </div>
        <div className="flex-1 overflow-y-auto">
          <MessageList messages={chatState.messages} />
        </div>
        <div className="border-t-2 border-gray-200 px-4 pt-4 mb-2 sm:mb-0">
          <MessageInput 
            service={service}
            isLoading={chatState.isLoading}
            isRecording={isRecording}
            startRecording={startRecording}
            input={input}
            setInput={setInput}
            error={chatState.error}
          />
        </div>
      </div>
    </main>
  );
}
