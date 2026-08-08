import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useFlights } from '../contexts/flight-context';
import WaveshareDisplay from '../components/WaveshareDisplay';
import FlightBoard from '../components/FlightBoard';
import './Tracker.css';

export default function Tracker() {
  const { flights, allTrackedFlights, sessionStats, loading, error } = useFlights();
  const [currentFlightIndex, setCurrentFlightIndex] = useState(0);
  const [sessionDuration, setSessionDuration] = useState('0m');

  useEffect(() => {
    if (flights.length <= 1) return;
    const interval = window.setInterval(() => {
      setCurrentFlightIndex((previous) => (previous + 1) % flights.length);
    }, 15000);
    return () => window.clearInterval(interval);
  }, [flights.length]);

  useEffect(() => {
    const updateDuration = () => {
      const elapsedMinutes = Math.floor(
        (Date.now() - new Date(sessionStats.sessionStart).getTime()) / 60000,
      );
      const hours = Math.floor(elapsedMinutes / 60);
      const minutes = elapsedMinutes % 60;
      setSessionDuration(hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`);
    };
    const initialUpdate = window.setTimeout(updateDuration, 0);
    const interval = window.setInterval(updateDuration, 60000);
    return () => {
      window.clearTimeout(initialUpdate);
      window.clearInterval(interval);
    };
  }, [sessionStats.sessionStart]);

  const currentFlight = flights.length
    ? flights[currentFlightIndex % flights.length]
    : null;

  return (
    <div className="tracker-page">
      <header className="tracker-hero">
        <div>
          <span className="eyebrow">Living room window</span>
          <h1>What’s outside right now.</h1>
          <p className="tracker-subtitle">
            A quiet view of the aircraft crossing your patch of sky.
          </p>
        </div>
        <div className="device-state">
          <span className={`status-light ${error ? 'error' : ''}`} aria-hidden="true" />
          <span>
            <strong>{error ? 'Needs attention' : 'Display online'}</strong>
            <small>{error ? 'The API could not be reached' : 'Checking every 15 seconds'}</small>
          </span>
        </div>
      </header>

      {loading && (
        <div className="tracker-loading">
          <div className="loading" />
          <p>Opening your view…</p>
        </div>
      )}

      {error && (
        <div className="tracker-error" role="alert">
          <div>
            <strong>We can’t reach the flight service.</strong>
            <p>{error}</p>
          </div>
          <button className="btn btn-primary" onClick={() => window.location.reload()}>
            Try again
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <section className="window-overview" aria-label="Current display">
            <div className="display-stage">
              <div className="stage-heading">
                <span>Live e-paper preview</span>
                <span>{flights.length} currently in view</span>
              </div>
              <WaveshareDisplay
                flight={currentFlight}
                showScanScreen={flights.length === 0}
              />
              {flights.length > 1 && (
                <p className="display-indicator">
                  Aircraft {currentFlightIndex + 1} of {flights.length}
                </p>
              )}
            </div>

            <aside className="session-panel">
              <div>
                <span className="eyebrow">This session</span>
                <p>Aircraft noticed since you opened this view.</p>
              </div>
              <dl>
                <div>
                  <dt>Detected</dt>
                  <dd>{sessionStats.flightsDetected}</dd>
                </div>
                <div>
                  <dt>Unique aircraft</dt>
                  <dd>{sessionStats.uniqueAircraft.size}</dd>
                </div>
                <div>
                  <dt>Watching for</dt>
                  <dd>{sessionDuration}</dd>
                </div>
              </dl>
              <Link to="/settings" className="text-link">Adjust this window view →</Link>
            </aside>
          </section>

          <section className="board-section">
            <FlightBoard flights={allTrackedFlights} currentFlights={flights} />
          </section>
        </>
      )}
    </div>
  );
}
