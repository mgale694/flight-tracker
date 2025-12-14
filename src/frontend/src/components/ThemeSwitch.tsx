/**
 * Theme switcher component
 */

import type { Theme } from '../theme';
import './ThemeSwitch.css';

interface ThemeSwitchProps {
  theme: Theme;
  onThemeChange: (theme: Theme) => void;
}

export function ThemeSwitch({ theme, onThemeChange }: ThemeSwitchProps) {
  const handleThemeChange = (newTheme: Theme) => {
    onThemeChange(newTheme);
  };

  return (
    <div className="theme-switch">
      <button
        className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
        onClick={() => handleThemeChange('light')}
        title="Light mode"
        aria-label="Light mode"
      >
        ☀️
      </button>
      <button
        className={`theme-btn ${theme === 'auto' ? 'active' : ''}`}
        onClick={() => handleThemeChange('auto')}
        title="Auto mode"
        aria-label="Auto mode"
      >
        🔄
      </button>
      <button
        className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
        onClick={() => handleThemeChange('dark')}
        title="Dark mode"
        aria-label="Dark mode"
      >
        🌙
      </button>
    </div>
  );
}
