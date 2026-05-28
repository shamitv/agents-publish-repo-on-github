import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../i18n/I18nContext';

export function LoginPage() {
  const { login } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [supplierId, setSupplierId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(supplierId, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || t('error_generic'));
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>{t('app_title')}</h1>
        <form onSubmit={handleSubmit}>
          <div className="login-field">
            <label>Supplier ID</label>
            <input
              type="text"
              value={supplierId}
              onChange={(e) => setSupplierId(e.target.value)}
              placeholder="supplier-001"
              required
            />
          </div>
          <div className="login-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="********"
              required
            />
          </div>
          {error && <p className="login-error">{error}</p>}
          <button type="submit" className="btn-login">{t('login_submit')}</button>
        </form>
      </div>
    </div>
  );
}
