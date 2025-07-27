import React from 'react';
import { setTheme, getTheme } from '../theme';

export const ThemeSwitch: React.FC = () => {
  const [currentTheme, setCurrentTheme] = React.useState<'light' | 'dark' | 'auto'>(getTheme());

  const handleThemeChange = (theme: 'light' | 'dark' | 'auto') => {
    setTheme(theme);
    setCurrentTheme(theme);
  };

  return (
    <div className="theme-switch">
      <label className="form-group">
        <span className="flight-detail-label">Theme</span>
        <select 
          value={currentTheme} 
          onChange={(e) => handleThemeChange(e.target.value as 'light' | 'dark' | 'auto')}
          className="theme-select"
        >
          <option value="auto">Auto (System)</option>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </label>
    </div>
  );
};
