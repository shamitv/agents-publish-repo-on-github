import React from 'react';
import { useTranslation, type Locale } from '../i18n/I18nContext';

export function Header() {
  const { t, locale, setLocale } = useTranslation();

  const toggleLocale = () => {
    setLocale(locale === 'en' ? 'es' as Locale : 'en' as Locale);
  };

  return (
    <header className="app-header">
      <h1>{t('app_title')}</h1>
      <nav>
        <a href="/">{t('nav_dashboard')}</a>
        <a href="/reports">{t('nav_reports')}</a>
        <a href="/webhooks">{t('nav_webhooks')}</a>
      </nav>
      <button
        className="locale-toggle"
        onClick={toggleLocale}
        aria-label={`Switch to ${locale === 'en' ? 'Spanish' : 'English'}`}
      >
        {locale === 'en' ? 'ES' : 'EN'}
      </button>
    </header>
  );
}