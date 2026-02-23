'use client';

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authApi } from '@/lib/api/auth';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  mustChangePassword: boolean;
  logout: () => Promise<void>;
  setAuthState: (isAuth: boolean, mustChange: boolean) => void;
  refreshAuthStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const PUBLIC_ROUTES = ['/login'];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [mustChangePassword, setMustChangePassword] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const checkAuthStatus = useCallback(async () => {
    if (PUBLIC_ROUTES.includes(pathname)) {
      setIsLoading(true);
      
      try {
        const { isAuthenticated: isAuth, mustChangePassword: mustChange } = await authApi.checkAuth();
        setIsAuthenticated(isAuth);
        setMustChangePassword(mustChange);
      } catch (error) {
        setIsAuthenticated(false);
        setMustChangePassword(false);
      } finally {
        setIsLoading(false);
      }
      
      return;
    }

    setIsLoading(true);

    try {
      const { isAuthenticated: isAuth, mustChangePassword: mustChange } = await authApi.checkAuth();
      
      setIsAuthenticated(isAuth);
      setMustChangePassword(mustChange);
      
      if (!isAuth) {
        router.push('/login');
      } else if (mustChange && pathname !== '/change-password') {
        router.push('/change-password');
      } else if (!mustChange && pathname === '/change-password') {
        router.push('/dashboard');
      }
    } catch (error) {
      setIsAuthenticated(false);
      setMustChangePassword(false);
      router.push('/login');
    } finally {
      setIsLoading(false);
    }
  }, [pathname, router]);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  const refreshAuthStatus = async () => {
    try {
      const { isAuthenticated: isAuth, mustChangePassword: mustChange } = await authApi.checkAuth();
      setIsAuthenticated(isAuth);
      setMustChangePassword(mustChange);
    } catch (error) {
      setIsAuthenticated(false);
      setMustChangePassword(false);
    }
  };

  const setAuthState = (isAuth: boolean, mustChange: boolean) => {
    setIsAuthenticated(isAuth);
    setMustChangePassword(mustChange);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsAuthenticated(false);
      setMustChangePassword(false);
      router.push('/login');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        mustChangePassword,
        logout,
        setAuthState,
        refreshAuthStatus,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}