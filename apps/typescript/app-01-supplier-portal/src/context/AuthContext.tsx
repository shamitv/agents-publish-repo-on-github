import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

interface AuthState {
  supplier_id: string;
  name: string;
  tier: string;
  token: string;
}

interface AuthContextType {
  user: AuthState | null;
  loading: boolean;
  login: (supplier_id: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('supplier_user');
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch { localStorage.removeItem('supplier_user'); }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (supplier_id: string, password: string) => {
    const response = await api.post('/portal/auth/login', { supplier_id, password });
    const { supplier } = response.data;
    const userData: AuthState = {
      supplier_id: supplier.supplier_id,
      name: supplier.name,
      tier: supplier.tier,
      token: supplier.token,
    };
    localStorage.setItem('auth_token', userData.token);
    localStorage.setItem('supplier_user', JSON.stringify(userData));
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('supplier_user');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
