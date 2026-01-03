/**
 * Error type definitions for better type safety.
 */

export interface ApiError {
  message: string;
  response?: {
    data?: {
      detail?: string;
      error?: string;
      message?: string;
    };
    status?: number;
  };
  request?: unknown;
}

export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as ApiError).message === 'string'
  );
}

export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.response?.data?.detail || error.response?.data?.error || error.response?.data?.message || error.message || 'An error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}

