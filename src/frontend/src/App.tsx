import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { useEffect } from 'react';
import './App.css';
import { initializeTheme, useTheme } from './theme';
import { ThemeSwitch } from './components/ThemeSwitch';
import { FlightProvider } from './contexts/FlightContext';
import Tracker from './pages/Tracker';
import Activities from './pages/Activities';
import Settings from './pages/Settings';
import Setup from './pages/Setup';

function App() {
  const [theme, setTheme] = useTheme();

  useEffect(() => {
    initializeTheme();
  }, []);

  return (
    <Router>
      <div className="app">
          <header className="app-header">
            <div className="header-content">
              <NavLink to="/" className="app-brand" aria-label="Flight Tracker home">
                <span className="brand-mark" aria-hidden="true">FT</span>
                <span>
                  <strong>Flight Tracker</strong>
                  <small>Your window to the sky</small>
                </span>
              </NavLink>
              <nav className="app-nav">
                <NavLink 
                  to="/" 
                  className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                  Window
                </NavLink>
                <NavLink 
                  to="/activities" 
                  className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                  History
                </NavLink>
                <NavLink 
                  to="/settings" 
                  className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                  Settings
                </NavLink>
              </nav>
              <NavLink to="/setup" className="setup-link">Add a display</NavLink>
              <ThemeSwitch theme={theme} onThemeChange={setTheme} />
            </div>
          </header>

          <main className="app-main">
            <Routes>
              <Route path="/" element={<FlightProvider><Tracker /></FlightProvider>} />
              <Route path="/activities" element={<Activities />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/setup" element={<Setup />} />
            </Routes>
          </main>

          <footer className="app-footer">
            <p>Quietly identifying the aircraft beyond your window.</p>
          </footer>
      </div>
    </Router>
  );
}

export default App;
