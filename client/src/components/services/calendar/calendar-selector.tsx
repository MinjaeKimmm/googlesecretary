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
      console.log('Calendar API response:', response.data);
      // Backend returns array of { id: string, summary: string }
      const calendarList = response.data.calendar_names || [];
      console.log('Calendar list:', calendarList);
      
      // Convert to Calendar objects using the actual IDs from the backend
      const converted = calendarList.map((calendar: { id: string; summary: string }) => {
        console.log('Processing calendar:', calendar);
        // Use the id field directly since backend sends it in correct format
        return {
          id: calendar.id,      // Use actual calendar ID from backend
          summary: calendar.summary
        };
      }) as Calendar[];
      
      // Set first calendar as default if none selected
      console.log('Converted calendars:', converted);
      console.log('Current calendar state:', calendarState);
      if (converted.length > 0 && !calendarState.selectedCalendarId) {
        console.log('Setting default calendar:', converted[0]);
        updateServiceSetup('calendar', { selectedCalendarId: converted[0].id });
      }
      
      return converted;
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

  // If no calendars available, show message
  if (calendars.length === 0) {
    return (
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-500">No calendars found</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3">
      <select
        value={calendarState.selectedCalendarId || calendars[0].id} // Fallback to first calendar if none selected
        onChange={(e) => {
          console.log('Calendar selection changed to:', e.target.value);
          updateServiceSetup('calendar', { selectedCalendarId: e.target.value });
        }}
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
