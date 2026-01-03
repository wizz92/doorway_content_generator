import api from './api';

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
      const response = await api.post<LoginResponse>('/api/auth/login', credentials);
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
      }
      return response.data;
    } catch (error: any) {
      console.error('Login API error:', error);
      // Re-throw with more details
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Login failed');
      } else if (error.request) {
        throw new Error('Network error: Could not reach server');
      } else {
        throw new Error('Login failed: ' + error.message);
      }
    }
  },

  async logout(): Promise<void> {
    try {
      await api.post('/api/auth/logout');
    } finally {
      localStorage.removeItem('auth_token');
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  },
};
