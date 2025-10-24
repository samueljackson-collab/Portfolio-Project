import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import api from '../api/client';

type AuthContextValue = {
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => !!localStorage.getItem('accessToken'));

  useEffect(() => {
    // Sync initial state when the provider is mounted in the browser.
    setIsAuthenticated(!!localStorage.getItem('accessToken'));
  }, []);

  const login = async (email: string, password: string) => {
    // Delegate the HTTP request to the shared API client so interceptors stay consistent.
    const response = await api.post('/auth/login', { email, password });
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('accessToken', access_token);
    localStorage.setItem('refreshToken', refresh_token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    // Removing tokens ensures the ProtectedRoute component blocks subsequent requests.
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setIsAuthenticated(false);
  };

  const value: AuthContextValue = { isAuthenticated, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
