import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { I18nProvider } from './i18n/I18nContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { SessionProvider } from './components/SessionProvider';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/Login';
import { DashboardPage } from './pages/DashboardPage';
import { ReportsPage } from './pages/ReportsPage';
import { ReportDetailPage } from './pages/ReportDetail';
import { WebhooksPage } from './pages/Webhooks';
import { TestWidgetsPage } from './pages/test/Widgets';
import { TestNotificationsPage } from './pages/test/Notifications';
import { TestConsolePage } from './pages/test/Console';
import { AdminFlagsPage } from './pages/admin/Flags';
import { AdminFlagDetailPage } from './pages/admin/FlagDetail';
import { AdminSchedulerPage } from './pages/admin/Scheduler';
import { AdminCachePage } from './pages/admin/Cache';
import './App.css';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div className="page-loading">Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/reports/:id" element={<ReportDetailPage />} />
        <Route path="/webhooks" element={<WebhooksPage />} />
        <Route path="/test/widgets" element={<TestWidgetsPage />} />
        <Route path="/test/notifications" element={<TestNotificationsPage />} />
        <Route path="/test/console" element={<TestConsolePage />} />
        <Route path="/admin/flags" element={<AdminFlagsPage />} />
        <Route path="/admin/flags/:key" element={<AdminFlagDetailPage />} />
        <Route path="/admin/scheduler" element={<AdminSchedulerPage />} />
        <Route path="/admin/cache" element={<AdminCachePage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <AuthProvider>
        <SessionProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </SessionProvider>
      </AuthProvider>
    </I18nProvider>
  );
}