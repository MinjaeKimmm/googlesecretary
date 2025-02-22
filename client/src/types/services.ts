export type ServiceType = 'calendar' | 'drive' | 'email';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface ServiceSetup {
  selectedCalendarId?: string;
  selectedFolderId?: string;
}

export interface ServiceState {
  calendar: {
    selectedCalendarId: string;
    chat: ChatState;
  };
  drive: {
    selectedFolderId: string;
    chat: ChatState;
  };
  email: {
    selectedFolderId: string;
    chat: ChatState;
  };
}
