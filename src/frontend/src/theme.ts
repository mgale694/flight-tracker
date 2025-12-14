/**
 * Theme management system with localStorage persistence
 */

export type Theme = 'light' | 'dark' | 'auto';

const THEME_STORAGE_KEY = 'flight-tracker-theme';

/**
 * Get the system's preferred color scheme
 */
export function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Get the current theme from localStorage or default to 'auto'
 */
export function getStoredTheme(): Theme {
  if (typeof window === 'undefined') return 'auto';
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === 'light' || stored === 'dark' || stored === 'auto') {
    return stored;
  }
  return 'auto';
}

/**
 * Store the theme preference in localStorage
 */
export function setStoredTheme(theme: Theme): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(THEME_STORAGE_KEY, theme);
}

/**
 * Get the effective theme (resolves 'auto' to 'light' or 'dark')
 */
export function getEffectiveTheme(theme: Theme): 'light' | 'dark' {
  if (theme === 'auto') {
    return getSystemTheme();
  }
  return theme;
}

/**
 * Apply the theme to the document
 */
export function applyTheme(theme: Theme): void {
  if (typeof document === 'undefined') return;
  
  const effectiveTheme = getEffectiveTheme(theme);
  document.documentElement.setAttribute('data-theme', effectiveTheme);
}

/**
 * Initialize theme on app load
 */
export function initTheme(): Theme {
  const storedTheme = getStoredTheme();
  applyTheme(storedTheme);
  return storedTheme;
}

/**
 * Initialize theme on app load (alias for initTheme)
 */
export function initializeTheme(): Theme {
  return initTheme();
}

/**
 * Set up listener for system theme changes
 */
export function watchSystemTheme(callback: () => void): () => void {
  if (typeof window === 'undefined') return () => {};
  
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handler = () => callback();
  mediaQuery.addEventListener('change', handler);
  
  // Return cleanup function
  return () => mediaQuery.removeEventListener('change', handler);
}

/**
 * React hook for theme management
 */
import { useState, useEffect } from 'react';

export function useTheme(): [Theme, (theme: Theme) => void] {
  const [theme, setThemeState] = useState<Theme>(() => getStoredTheme());

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    if (theme === 'auto') {
      const cleanup = watchSystemTheme(() => {
        applyTheme(theme);
      });
      return cleanup;
    }
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    setStoredTheme(newTheme);
    applyTheme(newTheme);
  };

  return [theme, setTheme];
}
