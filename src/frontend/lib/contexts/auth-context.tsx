'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useCallback,
} from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authApi } from '@/lib/api/auth';

interface AuthState {
  isAuthenticated: boolean;
  mustChangePassword: boolean;
}

interface AuthContextType extends AuthState {
  isLoading: boolean;
  logout: () => Promise<void>;
  setAuthState: (isAuth: boolean, mustChange: boolean) => void;
  refreshAuthStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const PUBLIC_ROUTES = ['/login'] as const;

const ROUTES = {
  LOGIN: '/login',
  CHANGE_PASSWORD: '/change-password',
  DASHBOARD: '/dashboard',
} as const;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthStateInternal] = useState<AuthState>({
    isAuthenticated: false,
    mustChangePassword: false,
  });
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const updateAuthState = useCallback((isAuth: boolean, mustChange: boolean) => {
    setAuthStateInternal({
      isAuthenticated: isAuth,
      mustChangePassword: mustChange,
    });
  }, []);

  const handleUnauthenticated = useCallback(() => {
    updateAuthState(false, false);
    if (!PUBLIC_ROUTES.includes(pathname as any)) {
      router.push(ROUTES.LOGIN);
    }
  }, [pathname, router, updateAuthState]);

  const handleAuthenticated = useCallback(
    (mustChange: boolean) => {
      updateAuthState(true, mustChange);

      if (mustChange && pathname !== ROUTES.CHANGE_PASSWORD) {
        router.push(ROUTES.CHANGE_PASSWORD);
      } else if (!mustChange && pathname === ROUTES.CHANGE_PASSWORD) {
        router.push(ROUTES.DASHBOARD);
      }
    },
    [pathname, router, updateAuthState]
  );

  const checkAuthStatus = useCallback(async () => {
    if (PUBLIC_ROUTES.includes(pathname as any)) {
      setIsLoading(true);

      try {
        const { isAuthenticated, mustChangePassword } = await authApi.checkAuth();
        updateAuthState(isAuthenticated, mustChangePassword);
      } catch {
        updateAuthState(false, false);
      } finally {
        setIsLoading(false);
      }

      return;
    }

    setIsLoading(true);

    try {
      const { isAuthenticated, mustChangePassword } = await authApi.checkAuth();

      if (!isAuthenticated) {
        handleUnauthenticated();
      } else {
        handleAuthenticated(mustChangePassword);
      }
    } catch {
      handleUnauthenticated();
    } finally {
      setIsLoading(false);
    }
  }, [pathname, handleUnauthenticated, handleAuthenticated, updateAuthState]);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  const refreshAuthStatus = async () => {
    try {
      const { isAuthenticated, mustChangePassword } = await authApi.checkAuth();
      updateAuthState(isAuthenticated, mustChangePassword);
    } catch {
      updateAuthState(false, false);
    }
  };

  const setAuthState = (isAuth: boolean, mustChange: boolean) => {
    updateAuthState(isAuth, mustChange);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      updateAuthState(false, false);
      router.push(ROUTES.LOGIN);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        isLoading,
        logout,
        setAuthState,
        refreshAuthStatus,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  
  return context;
}