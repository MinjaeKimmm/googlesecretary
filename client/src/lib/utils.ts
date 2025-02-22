export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

export function createSafeFileName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function getServiceLabel(service: string): string {
  const labels = {
    calendar: 'Calendar',
    drive: 'Drive',
    email: 'Email'
  };
  return labels[service as keyof typeof labels] || service;
}
