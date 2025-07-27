import React from 'react';
import { setTheme, getTheme, getCurrentEffectiveTheme } from '../theme';

export const ThemeSwitch: React.FC = () => {
  const [currentTheme, setCurrentTheme] = React.useState<'light' | 'dark'>(() => {
    // Initialize based on system preference if no saved theme
    const savedTheme = getTheme();
    if (savedTheme === 'auto') {
      return getCurrentEffectiveTheme();
    }
    return savedTheme;
  });

  // Set initial theme based on system preference if needed
  React.useEffect(() => {
    const savedTheme = getTheme();
    if (savedTheme === 'auto') {
      const systemTheme = getCurrentEffectiveTheme();
      setTheme(systemTheme);
      setCurrentTheme(systemTheme);
    }
  }, []);

  const handleThemeToggle = () => {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    setCurrentTheme(newTheme);
  };

  const getThemeIcon = () => {
    return currentTheme === 'dark' ? '🌙' : '☀️';
  };

  const getThemeLabel = () => {
    return currentTheme === 'dark' ? 'Dark' : 'Light';
  };

  return (
    <button
      onClick={handleThemeToggle}
      className="theme-toggle-button"
      title={`Current theme: ${getThemeLabel()}. Click to switch to ${currentTheme === 'light' ? 'Dark' : 'Light'} mode.`}
      aria-label={`Switch to ${currentTheme === 'light' ? 'dark' : 'light'} theme. Current: ${getThemeLabel()}`}
    >
      <span className="theme-icon">{getThemeIcon()}</span>
      <span className="theme-label">{getThemeLabel()}</span>
    </button>
  );
};
