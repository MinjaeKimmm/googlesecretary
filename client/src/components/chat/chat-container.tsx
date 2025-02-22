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
  language: string;
}

export function ChatContainer({ service, language }: ChatContainerProps) {
  const { serviceStates } = useServiceStore();
  const chatState = serviceStates[service].chat;
  const [isRecording, setIsRecording] = useState(false);
  const [speechRecognition, setSpeechRecognition] = useState<SpeechRecognition | null>(null);
  const [input, setInput] = useState(""); 
  const [selectedCharacter, setSelectedCharacter] = useState("Bunny"); // ✅ 기본 캐릭터 설정
  const [showDropdown, setShowDropdown] = useState(false); // ✅ 드롭다운 표시 여부

  // 🎤 음성 인식 초기화 (언어 변경 시 재설정)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognitionAPI =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognitionAPI) {
        const recognition = new SpeechRecognitionAPI();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = language;
        setSpeechRecognition(recognition);
      }
    }
  }, [language]);

  // 🎤 음성 녹음 시작 함수
  const startRecording = () => {
    if (!speechRecognition) return;

    setIsRecording(true);
    speechRecognition.start();

    speechRecognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      console.log(`🎙️ [${language}] 음성 인식 결과:`, transcript);
      setInput(transcript);
    };

    speechRecognition.onend = () => {
      setIsRecording(false);
    };

    speechRecognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error("Speech recognition error:", event);
      setIsRecording(false);
    };
  };

  return (
    <div className="relative flex flex-col h-[600px] border border-gray-200 rounded-lg bg-white">
      {/* ✅ 우측 상단 캐릭터 변경 버튼 */}
      <div className="absolute top-2 right-4 z-10">
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="bg-gray-800 text-white px-4 py-2 rounded-md shadow-md hover:bg-gray-700 transition"
        >
          캐릭터 변경 ⬇️
        </button>

        {showDropdown && (
          <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-300 rounded-md shadow-lg">
            {["Bunny", "Shortcut", "Wolf", "Teenager", "Tuxedo", "Yukata"].map((character) => (
              <button
                key={character}
                onClick={() => {
                  setSelectedCharacter(character);
                  setShowDropdown(false);
                }}
                className={`block w-full px-4 py-2 text-left text-gray-800 hover:bg-gray-100 ${
                  selectedCharacter === character ? "font-bold text-blue-600" : ""
                }`}
              >
                {character}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 캐릭터 뷰어 */}
      <div className="h-1/2 w-full">
        <VrmViewer selectedCharacter={selectedCharacter} />
      </div>

      <div className="h-1/2 overflow-y-auto">
        <MessageList messages={chatState.messages} selectedCharacter={selectedCharacter} />
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
  );
}
