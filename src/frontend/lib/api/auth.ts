import { apiClient } from './client';

export interface LoginResponse {
  message: string;
  must_change_password: boolean;
}

export interface ChangePasswordResponse {
  message: string;
}

export interface AuthStatusResponse {
  isAuthenticated: boolean;
  mustChangePassword: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const HTTP_STATUS = {
  OK: 200,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  SERVER_ERROR: 500,
} as const;

export const authApi = {
  async login(password: string): Promise<LoginResponse> {
    return apiClient.post<LoginResponse>('/api/auth/login', { password });
  },

  async changePassword(
    newPassword: string,
    confirmPassword: string
  ): Promise<ChangePasswordResponse> {
    return apiClient.post<ChangePasswordResponse>('/api/auth/change-password', {
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
  },

  async logout(): Promise<void> {
    return apiClient.post<void>('/api/auth/logout');
  },

  async checkAuth(): Promise<AuthStatusResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
        method: 'GET',
        credentials: 'include',
      });

      return authApi._parseAuthResponse(response);
    } catch {
      return { isAuthenticated: false, mustChangePassword: false };
    }
  },

  _parseAuthResponse(response: Response): AuthStatusResponse {
    if (response.status === HTTP_STATUS.UNAUTHORIZED) {
      return { isAuthenticated: false, mustChangePassword: false };
    }

    if (response.status === HTTP_STATUS.FORBIDDEN) {
      return { isAuthenticated: true, mustChangePassword: true };
    }

    if (response.ok) {
      return { isAuthenticated: true, mustChangePassword: false };
    }

    if (response.status >= HTTP_STATUS.SERVER_ERROR) {
      return { isAuthenticated: false, mustChangePassword: false };
    }

    return { isAuthenticated: false, mustChangePassword: false };
  },
} as const;