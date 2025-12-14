import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { useEffect } from 'react';
import './App.css';
import { initializeTheme, useTheme } from './theme';
import { ThemeSwitch } from './components/ThemeSwitch';
import { FlightProvider } from './contexts/FlightContext';
import Tracker from './pages/Tracker';
import Activities from './pages/Activities';
import Settings from './pages/Settings';

function App() {
  const [theme, setTheme] = useTheme();

  useEffect(() => {
    initializeTheme();
  }, []);

  return (
    <Router>
      <FlightProvider>
        <div className="app">
          <header className="app-header">
            <div className="header-content">
              <h1 className="app-title">✈️ Flight Tracker</h1>
              <nav className="app-nav">
                <NavLink 
                  to="/" 
                  className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                  Tracker
                </NavLink>
                <NavLink 
                  to="/activities" 
                  className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                  Activities
                </NavLink>
                <NavLink 
                  to="/settings" 
                  className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
                >
                  Settings
                </NavLink>
              </nav>
              <ThemeSwitch theme={theme} onThemeChange={setTheme} />
            </div>
          </header>

          <main className="app-main">
            <Routes>
              <Route path="/" element={<Tracker />} />
              <Route path="/activities" element={<Activities />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>

          <footer className="app-footer">
            <p>Flight Tracker v1.0.0 | Powered by FlightRadar24</p>
          </footer>
        </div>
      </FlightProvider>
    </Router>
  );
}

export default App;
