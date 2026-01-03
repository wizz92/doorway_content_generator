import axios from 'axios';
import { handleApiError } from '../utils/errorUtils';

// Use relative URL in development (Vite proxy) or full URL in production
const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : 'http://localhost:8001');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Set to false when using Vite proxy
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
    }
    // Use utility function for error handling
    const errorMessage = handleApiError(error);
    return Promise.reject(new Error(errorMessage));
  }
);

export default api;
