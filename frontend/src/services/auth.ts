import api from './api';

import { logger } from '../utils/logger';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: {
    id: number;
    username: string;
    created_at: string;
    last_login: string | null;
  };
}

export interface User {
  id: number;
  username: string;
  created_at: string;
  last_login: string | null;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/auth/login', credentials);
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
      }
      return response.data;
    } catch (error: unknown) {
      logger.error('Login API error:', error);
      const err = error as { response?: { data?: { detail?: string } }; request?: unknown; message?: string };
      if (err.response) {
        throw new Error(err.response.data?.detail || 'Login failed');
      } else if (err.request) {
        throw new Error('Network error: Could not reach server');
      } else {
        throw new Error('Login failed: ' + (err.message || 'Unknown error'));
      }
    }
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } finally {
      localStorage.removeItem('auth_token');
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  },
};
