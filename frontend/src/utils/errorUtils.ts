import axios from 'axios';

import { ApiError } from '../types/api';

/**
 * Extract error message from API error.
 * This is a convenience function that wraps handleApiError for simpler use cases.
 */
export function extractErrorMessage(error: unknown): string {
  return handleApiError(error);
}

/**
 * Handle API error and return user-friendly message.
 * This is the main error handling function that should be used throughout the app.
 */
export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    // Handle specific status codes
    if (error.response?.status === 401) {
      return 'Authentication required. Please log in.';
    }
    
    if (error.response?.status === 403) {
      return 'Access denied. You do not have permission to perform this action.';
    }
    
    if (error.response?.status === 404) {
      return 'Resource not found.';
    }
    
    if (error.response?.status === 500) {
      return 'Server error. Please try again later.';
    }
    
    // Extract error message from response
    const apiError = error.response?.data as ApiError | undefined;
    return apiError?.detail || apiError?.message || error.message || 'An error occurred';
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
}

