'use client';

import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useServiceStore } from '@/stores/service-store';
import apiClient from '@/lib/api-client';
import { useSession } from 'next-auth/react';

interface Calendar {
  id: string;
  summary: string;
}

export function CalendarSelector() {
  const { data: session } = useSession();
  const { serviceStates, updateServiceSetup } = useServiceStore();
  const calendarState = serviceStates.calendar;

  const { data: calendars = [], isLoading } = useQuery({
    queryKey: ['calendars'],
    queryFn: async () => {
      const response = await apiClient.get('/api/calendar/list');
      // The FastAPI endpoint returns calendar_names as array of {calendar_id: calendar_name}
      const calendarList = response.data.calendar_names || [];
      // Convert to Calendar objects
      return calendarList.map((calendar: { [key: string]: string }) => {
        const [id] = Object.keys(calendar);
        return {
          id,
          summary: calendar[id]
        };
      }) as Calendar[];
    },
    enabled: !!session?.accessToken
  });

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
        <span className="text-sm text-gray-500">Loading calendars...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3">
      <select
        value={calendarState.selectedCalendarId}
        onChange={(e) => updateServiceSetup('calendar', { selectedCalendarId: e.target.value })}
        className="form-select rounded-lg border-gray-300 text-sm"
      >
        {calendars.map((calendar) => (
          <option key={calendar.id} value={calendar.id}>
            {calendar.summary}
          </option>
        ))}
      </select>
    </div>
  );
}
