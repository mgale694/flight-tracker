// Theme configuration types for Flight Tracker

declare const __THEME_COLORS__: {
  primary: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
};

// Export theme colors for use in components
export const THEME_COLORS = __THEME_COLORS__;

// CSS Custom Property helpers
export const getCSSVar = (varName: string): string => {
  return `var(--${varName})`;
};

export const setCSSVar = (varName: string, value: string): void => {
  document.documentElement.style.setProperty(`--${varName}`, value);
};

// Theme utilities
export const theme = {
  colors: {
    primary: getCSSVar('primary-color'),
    primaryHover: getCSSVar('primary-hover'),
    secondary: getCSSVar('secondary-color'),
    success: getCSSVar('success-color'),
    successHover: getCSSVar('success-hover'),
    warning: getCSSVar('warning-color'),
    danger: getCSSVar('danger-color'),
    info: getCSSVar('info-color'),
    
    // Backgrounds
    bgPrimary: getCSSVar('bg-primary'),
    bgSecondary: getCSSVar('bg-secondary'),
    bgDark: getCSSVar('bg-dark'),
    bgDarker: getCSSVar('bg-darker'),
    
    // Text
    textPrimary: getCSSVar('text-primary'),
    textSecondary: getCSSVar('text-secondary'),
    textLight: getCSSVar('text-light'),
    textMuted: getCSSVar('text-muted'),
    
    // Borders
    borderColor: getCSSVar('border-color'),
    borderFocus: getCSSVar('border-focus'),
  },
  
  spacing: {
    xs: getCSSVar('spacing-xs'),
    sm: getCSSVar('spacing-sm'),
    md: getCSSVar('spacing-md'),
    lg: getCSSVar('spacing-lg'),
    xl: getCSSVar('spacing-xl'),
  },
  
  radius: {
    sm: getCSSVar('radius-sm'),
    md: getCSSVar('radius-md'),
    lg: getCSSVar('radius-lg'),
  },
  
  fontSize: {
    sm: getCSSVar('font-size-sm'),
    base: getCSSVar('font-size-base'),
    lg: getCSSVar('font-size-lg'),
    xl: getCSSVar('font-size-xl'),
    xxl: getCSSVar('font-size-xxl'),
  },
  
  fontFamily: {
    base: getCSSVar('font-family'),
    mono: getCSSVar('font-family-mono'),
  },
  
  transition: {
    fast: getCSSVar('transition-fast'),
    normal: getCSSVar('transition-normal'),
  },
  
  shadows: {
    sm: getCSSVar('shadow-sm'),
    md: getCSSVar('shadow-md'),
    focus: getCSSVar('shadow-focus'),
  },
  
  layout: {
    maxWidth: getCSSVar('max-width'),
    navbarHeight: getCSSVar('navbar-height'),
  },
};

// Theme switching utilities
export const setTheme = (themeName: 'light' | 'dark' | 'auto') => {
  const root = document.documentElement;
  
  if (themeName === 'auto') {
    root.removeAttribute('data-theme');
  } else {
    root.setAttribute('data-theme', themeName);
  }
  
  // Store preference
  localStorage.setItem('flight-tracker-theme', themeName);
};

export const getTheme = (): 'light' | 'dark' | 'auto' => {
  return (localStorage.getItem('flight-tracker-theme') as 'light' | 'dark' | 'auto') || 'auto';
};

// Initialize theme on app start
export const initializeTheme = () => {
  const savedTheme = getTheme();
  setTheme(savedTheme);
};
