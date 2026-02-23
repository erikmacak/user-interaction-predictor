import { apiClient, ApiError } from './client';

export interface LoginResponse {
  message: string;
  must_change_password: boolean;
}

export interface ChangePasswordResponse {
  message: string;
}

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

  async checkAuth(): Promise<{ isAuthenticated: boolean; mustChangePassword: boolean }> {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/verify`, {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.status === 401) {
        return { isAuthenticated: false, mustChangePassword: false };
      }
      
      if (response.status === 403) {
        return { isAuthenticated: true, mustChangePassword: true };
      }
      
      if (response.ok) {
        return { isAuthenticated: true, mustChangePassword: false };
      }
      
      if (response.status >= 500) {
        return { isAuthenticated: false, mustChangePassword: false };
      }
      
      return { isAuthenticated: false, mustChangePassword: false };
    } catch (error) {
      return { isAuthenticated: false, mustChangePassword: false };
    }
  },
};