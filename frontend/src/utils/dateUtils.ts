/**
 * Format a date string to locale string.
 * Handles invalid dates gracefully.
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) {
    return 'Unknown';
  }
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Unknown';
    }
    return date.toLocaleString();
  } catch {
    return 'Unknown';
  }
}

/**
 * Format a date string to ISO string.
 */
export function formatDateISO(dateString: string | null | undefined): string {
  if (!dateString) {
    return '';
  }
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return '';
    }
    return date.toISOString();
  } catch {
    return '';
  }
}

/**
 * Get relative time string (e.g., "2 hours ago").
 */
export function getRelativeTime(dateString: string | null | undefined): string {
  if (!dateString) {
    return 'Unknown';
  }
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Unknown';
    }
    
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSecs < 60) {
      return 'Just now';
    } else if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      return formatDate(dateString);
    }
  } catch {
    return 'Unknown';
  }
}

