import { JobStatus } from '../types/job';
import { AccessTime, CheckCircle, Error as ErrorIcon } from '@mui/icons-material';
import { SvgIconComponent } from '@mui/icons-material';

/**
 * Get status color for Material-UI components.
 */
export function getStatusColor(status: JobStatus | string | undefined): 'default' | 'success' | 'info' | 'error' {
  if (!status) {
    return 'default';
  }
  
  const statusLower = String(status).toLowerCase().trim();
  
  switch (statusLower) {
    case 'completed':
      return 'success';
    case 'processing':
      return 'info';
    case 'failed':
      return 'error';
    default:
      return 'default';
  }
}

/**
 * Get status icon component.
 */
export function getStatusIcon(status: JobStatus | string | undefined): SvgIconComponent {
  if (!status) {
    return AccessTime;
  }
  
  const statusLower = String(status).toLowerCase().trim();
  
  switch (statusLower) {
    case 'completed':
      return CheckCircle;
    case 'failed':
      return ErrorIcon;
    default:
      return AccessTime;
  }
}

/**
 * Format status text with capitalization.
 */
export function formatStatus(status: JobStatus | string | undefined): string {
  if (!status) {
    return 'Unknown';
  }
  
  const statusLower = String(status).toLowerCase().trim();
  return statusLower.charAt(0).toUpperCase() + statusLower.slice(1);
}

/**
 * Get status display text for progress.
 */
export function getStatusDisplayText(status: JobStatus | string | undefined): string {
  if (!status) {
    return 'In Progress';
  }
  
  const statusLower = String(status).toLowerCase().trim();
  
  switch (statusLower) {
    case 'processing':
      return 'Processing';
    case 'queued':
      return 'Queued';
    default:
      return 'In Progress';
  }
}

