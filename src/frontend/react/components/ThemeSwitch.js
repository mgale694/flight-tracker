// Theme switching utilities
function setTheme(themeName) {
  const root = document.documentElement;
  root.setAttribute('data-theme', themeName);
  
  // Store preference
  localStorage.setItem('flight-tracker-theme', themeName);
}

function getTheme() {
  const saved = localStorage.getItem('flight-tracker-theme');
  return saved || 'auto'; // Return 'auto' for migration purposes
}

// Get the currently effective theme (resolves 'auto' to 'light' or 'dark')
function getCurrentEffectiveTheme() {
  const currentTheme = getTheme();
  
  if (currentTheme === 'auto') {
    // Check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  
  return currentTheme;
}

// Initialize theme on app start
function initializeTheme() {
  const savedTheme = getTheme();
  
  // If saved theme is 'auto' or doesn't exist, use system preference
  if (savedTheme === 'auto') {
    const systemTheme = getCurrentEffectiveTheme();
    setTheme(systemTheme);
  } else {
    setTheme(savedTheme);
  }
}

function ThemeSwitch() {
  const [currentTheme, setCurrentTheme] = React.useState(() => {
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
    // Show icon for what mode it will switch TO, not current mode
    return currentTheme === 'dark' ? '☀️' : '🌙';
  };

  const getThemeLabel = () => {
    return currentTheme === 'dark' ? 'Light' : 'Dark';
  };

  return React.createElement(
    'button',
    {
      onClick: handleThemeToggle,
      className: 'theme-switch',
      title: `Current theme: ${getThemeLabel()}. Click to switch to ${currentTheme === 'light' ? 'Dark' : 'Light'} mode.`,
      'aria-label': `Switch to ${currentTheme === 'light' ? 'dark' : 'light'} theme. Current: ${getThemeLabel()}`
    },
    React.createElement('span', { className: 'theme-icon' }, getThemeIcon()),
    React.createElement('span', { className: 'theme-label' }, getThemeLabel())
  );
}

// Export to global namespace
window.ThemeSwitch = ThemeSwitch;
window.initializeTheme = initializeTheme;
