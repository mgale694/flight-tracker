function App() {
  const [currentPage, setCurrentPage] = React.useState('tracker');

  React.useEffect(() => {
    // Initialize theme
    if (window.initializeTheme) {
      window.initializeTheme();
    }
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'tracker':
        return React.createElement(window.Tracker);
      case 'activities':
        return React.createElement(window.Activities);
      case 'settings':
        return React.createElement(window.Settings);
      default:
        return React.createElement(window.Tracker);
    }
  };

  const handleNavClick = (page) => {
    setCurrentPage(page);
  };

  return React.createElement(
    'div',
    { className: 'App' },
    React.createElement(
      'nav',
      { className: 'navbar' },
      React.createElement(
        'div',
        { className: 'nav-container' },
        React.createElement(
          'div',
          { className: 'nav-logo' },
          React.createElement('span', { className: 'logo-icon' }, '✈️'),
          'Flight Tracker'
        ),
        React.createElement(
          'div',
          { className: 'nav-links' },
          React.createElement(
            'a',
            {
              href: '#',
              className: `nav-link ${currentPage === 'tracker' ? 'active' : ''}`,
              onClick: (e) => {
                e.preventDefault();
                handleNavClick('tracker');
              }
            },
            'Display'
          ),
          React.createElement(
            'a',
            {
              href: '#',
              className: `nav-link ${currentPage === 'activities' ? 'active' : ''}`,
              onClick: (e) => {
                e.preventDefault();
                handleNavClick('activities');
              }
            },
            'Activities'
          ),
          React.createElement(
            'a',
            {
              href: '#',
              className: `nav-link ${currentPage === 'settings' ? 'active' : ''}`,
              onClick: (e) => {
                e.preventDefault();
                handleNavClick('settings');
              }
            },
            'Settings'
          ),
          React.createElement(window.ThemeSwitch)
        )
      )
    ),
    React.createElement(
      'main',
      { className: 'main-content' },
      renderPage()
    ),
    React.createElement(
      'footer',
      { className: 'footer' },
      React.createElement('p', null, '© 2024 Flight Tracker - Raspberry Pi Flight Tracking System')
    )
  );
}

window.App = App;