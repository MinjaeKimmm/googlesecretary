import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { ServiceType, Message } from '@/types/services';
import apiClient from '@/lib/api-client';
import { useServiceStore } from '@/stores/service-store';

export function useChat(service: ServiceType) {
  const { data: session } = useSession();
  const { addMessage, setLoading, setError, serviceStates } = useServiceStore();
  const [isProcessing, setIsProcessing] = useState(false);

  const sendMessage = async (content: string) => {
    if (!session?.accessToken || isProcessing) return;

    try {
      setIsProcessing(true);
      setLoading(service, true);

      // Add user message immediately
      const userMessage: Message = { role: 'user', content };
      addMessage(service, userMessage);

      // Prepare payload based on service type
      let payload: any = { message: content };
      
      if (service === 'calendar') {
        const calendarId = serviceStates.calendar.selectedCalendarId;
        if (!calendarId) {
          throw new Error('Please select a calendar first');
        }
        payload = {
          user_message: content,
          calendar_id: calendarId
        };
      }

      console.log('Sending chat request with payload:', payload);

      const response = await apiClient.post(
        `/api/${service}/chat`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${session.accessToken}`
          }
        }
      );

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.message
      };
      addMessage(service, assistantMessage);
    } catch (error) {
      setError(service, 'Failed to send message');
    } finally {
      setLoading(service, false);
      setIsProcessing(false);
    }
  };

  return {
    sendMessage,
    isProcessing
  };
}
