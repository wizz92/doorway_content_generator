/**
 * Error type definitions for better type safety.
 * Re-exports ApiError from api.ts for consistency.
 */

export { ApiError } from './api';

/**
 * Type guard to check if error is an axios error with API error response.
 */
export function isAxiosApiError(error: unknown): error is {
  response?: {
    data?: {
      detail?: string;
      error?: string;
      message?: string;
    };
    status?: number;
  };
  message?: string;
} {
  return (
    typeof error === 'object' &&
    error !== null &&
    'response' in error
  );
}

