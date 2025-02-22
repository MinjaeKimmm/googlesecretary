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

export interface ServiceStatus {
  is_setup: boolean;
  last_setup_time: string | null;
  scope_version: string;
}

export interface UserServices {
  calendar?: ServiceStatus;
  email?: ServiceStatus;
  drive?: ServiceStatus;
}

export interface UserData {
  email: string;
  services: UserServices;
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
