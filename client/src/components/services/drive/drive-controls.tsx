'use client';

import * as React from 'react';
import { ServiceStatus } from '../shared/service-status';
import { FolderSelector } from './folder-selector';

export function DriveControls() {
  return (
    <div className="flex items-center space-x-4">
      <ServiceStatus service="drive" />
      <FolderSelector />
    </div>
  );
}
