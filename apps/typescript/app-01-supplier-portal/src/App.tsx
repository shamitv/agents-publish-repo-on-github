import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { I18nProvider } from './i18n/I18nContext';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { ReportsPage } from './pages/ReportsPage';
import './App.css';

export default function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <div className="app">
          <Header />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/webhooks" element={<DashboardPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </I18nProvider>
  );
}