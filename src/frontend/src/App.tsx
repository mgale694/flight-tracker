import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { useEffect } from 'react';
import './App.css';
import { initializeTheme, useTheme } from './theme';
import { ThemeSwitch } from './components/ThemeSwitch';
import Tracker from './pages/Tracker';
import Activities from './pages/Activities';

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
            </nav>
            <ThemeSwitch theme={theme} onThemeChange={setTheme} />
          </div>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Tracker />} />
            <Route path="/activities" element={<Activities />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>Flight Tracker v1.0.0 | Powered by FlightRadar24</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
