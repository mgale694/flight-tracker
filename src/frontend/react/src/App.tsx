import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Tracker } from './pages/Tracker';
import { Activities } from './pages/Activities';
import { Settings } from './components/Settings';
import { ThemeSwitch } from './components/ThemeSwitch';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <div className="nav-logo">
              <span className="logo-icon">✈️</span>
              Flight Tracker
            </div>
            <div className="nav-links">
              <Link to="/" className="nav-link">
                Display
              </Link>
              <Link to="/activities" className="nav-link">
                Activities
              </Link>
              <Link to="/settings" className="nav-link">
                Settings
              </Link>
              <ThemeSwitch />
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Tracker />} />
            <Route path="/activities" element={<Activities />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>&copy; 2024 Flight Tracker - Raspberry Pi Flight Tracking System</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
