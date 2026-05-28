import React, { useEffect } from 'react';
import api from '../services/api';

// DECOY: Simulates short-lived token with automatic refresh interceptor
// Looks like it could be bypassed, but properly refreshes within 5-minute window
export function SessionProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const interval = setInterval(() => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        api.post('/portal/auth/verify', { token }).catch(() => {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('supplier_user');
          window.location.href = '/login';
        });
      }
    }, 300000);

    return () => clearInterval(interval);
  }, []);

  return <>{children}</>;
}
