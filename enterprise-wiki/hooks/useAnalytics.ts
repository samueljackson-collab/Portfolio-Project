import { useEffect } from 'react';

interface AnalyticsEvent {
  category: string;
  action: string;
  label?: string;
  value?: number;
}

export const useAnalytics = () => {
  useEffect(() => {
    // Track page views
    const trackPageView = () => {
      const page = window.location.hash || '#/';
      console.log('[Analytics] Page view:', page);
      // In production, send to your analytics service
      // Example: gtag('event', 'page_view', { page_path: page });
    };

    trackPageView();
    window.addEventListener('hashchange', trackPageView);

    return () => {
      window.removeEventListener('hashchange', trackPageView);
    };
  }, []);

  const trackEvent = ({ category, action, label, value }: AnalyticsEvent) => {
    console.log('[Analytics] Event:', { category, action, label, value });
    // In production, send to analytics service
    // Example: gtag('event', action, { event_category: category, event_label: label, value });
  };

  return { trackEvent };
};
