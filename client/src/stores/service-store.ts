import { create } from 'zustand';
import { ServiceType, ServiceState, Message, ServiceSetup } from '@/types/services';

interface StoreState {
  activeService: ServiceType;
  serviceStates: ServiceState;
  setActiveService: (service: ServiceType) => void;
  updateServiceSetup: (service: ServiceType, setup: Partial<ServiceSetup>) => void;
  addMessage: (service: ServiceType, message: Message) => void;
  setLoading: (service: ServiceType, isLoading: boolean) => void;
  setError: (service: ServiceType, error: string | null) => void;
}

const getInitialMessages = (service: ServiceType): Message[] => ({
  calendar: [{ role: 'assistant' as const, content: "👋 Hi! I'm your Calendar Assistant. How can I help you manage your schedule?" }],
  drive: [{ role: 'assistant' as const, content: "👋 Hi! I'm your Drive Assistant. I can help you manage your files and folders." }],
  email: [{ role: 'assistant' as const, content: "👋 Hi! I'm your Email Assistant. Need help with your emails?" }]
}[service]);

const initialState: ServiceState = {
  calendar: {
    selectedCalendarId: '',  // No default calendar, will be set after fetching
    chat: { messages: getInitialMessages('calendar'), isLoading: false, error: null }
  },
  drive: {
    selectedFolderId: 'root',
    selectedFolderPath: 'My Drive',
    chat: { messages: getInitialMessages('drive'), isLoading: false, error: null }
  },
  email: {
    selectedFolderId: 'INBOX',
    chat: { messages: getInitialMessages('email'), isLoading: false, error: null }
  }
};

export const useServiceStore = create<StoreState>((set) => ({
  activeService: 'calendar',
  serviceStates: initialState,

  setActiveService: (service) => set({ activeService: service }),

  updateServiceSetup: (service, setup) => set((state) => ({
    serviceStates: {
      ...state.serviceStates,
      [service]: { ...state.serviceStates[service], ...setup }
    }
  })),

  addMessage: (service, message) => set((state) => ({
    serviceStates: {
      ...state.serviceStates,
      [service]: {
        ...state.serviceStates[service],
        chat: {
          ...state.serviceStates[service].chat,
          messages: [...state.serviceStates[service].chat.messages, message]
        }
      }
    }
  })),

  setLoading: (service, isLoading) => set((state) => ({
    serviceStates: {
      ...state.serviceStates,
      [service]: {
        ...state.serviceStates[service],
        chat: { ...state.serviceStates[service].chat, isLoading }
      }
    }
  })),

  setError: (service, error) => set((state) => ({
    serviceStates: {
      ...state.serviceStates,
      [service]: {
        ...state.serviceStates[service],
        chat: { ...state.serviceStates[service].chat, error }
      }
    }
  }))
}));
