'use client';

import * as React from 'react';
import { ServiceStatus } from '../shared/service-status';

export function EmailControls() {
  return (
    <div className="flex items-center space-x-4">
      <ServiceStatus service="email" />
    </div>
  );
}
