/**
 * Tracker page - Main dashboard with display and flight board
 */

import { useState, useEffect } from 'react';
import type { Flight } from '../types';
import { useFlights } from '../contexts/FlightContext';
import WaveshareDisplay from '../components/WaveshareDisplay';
import FlightBoard from '../components/FlightBoard';
import './Tracker.css';

export default function Tracker() {
  const {
    flights,
    allTrackedFlights,
    sessionStats,
    loading,
    error,
    displayHoldTime,
    lastFlight,
    lastFlightTime,
  } = useFlights();

  const [currentFlightIndex, setCurrentFlightIndex] = useState(0);

  // Rotate through flights on display
  useEffect(() => {
    if (flights.length === 0) return;

    const interval = setInterval(() => {
      setCurrentFlightIndex(prev => (prev + 1) % flights.length);
    }, 5000); // Rotate every 5 seconds

    return () => clearInterval(interval);
  }, [flights.length]);

  const getSessionDuration = () => {
    const start = new Date(sessionStats.sessionStart);
    const now = new Date();
    const diffMs = now.getTime() - start.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const mins = diffMins % 60;
    
    if (diffHours > 0) {
      return `${diffHours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  // Determine which flight to display
  // Use current flight if available, otherwise use last flight if within hold time
  const getDisplayFlight = (): Flight | null => {
    if (flights.length > 0) {
      return flights[currentFlightIndex];
    }
    
    // Check if we should still display the last flight
    if (lastFlight && lastFlightTime) {
      const secondsSinceLastFlight = (Date.now() - lastFlightTime) / 1000;
      if (secondsSinceLastFlight < displayHoldTime) {
        return lastFlight;
      }
    }
    
    return null;
  };

  const currentFlight = getDisplayFlight();

  return (
    <div className="tracker-page">
      <div className="tracker-header">
        <div>
          <h1>Flight Tracker</h1>
          <p className="tracker-subtitle">Real-time aircraft tracking dashboard</p>
        </div>
        {!loading && (
          <div className="session-info">
            <div className="stat">
              <span className="stat-label">Detected:</span>
              <span className="stat-value">{sessionStats.flightsDetected}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Unique:</span>
              <span className="stat-value">{sessionStats.uniqueAircraft.size}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Duration:</span>
              <span className="stat-value">{getSessionDuration()}</span>
            </div>
          </div>
        )}
      </div>

      {loading && (
        <div className="tracker-loading">
          <div className="loading"></div>
          <p>Loading flight data...</p>
        </div>
      )}

      {error && (
        <div className="tracker-error">
          <p>❌ {error}</p>
          <button className="btn btn-primary" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="display-section">
            <WaveshareDisplay
              flight={currentFlight}
              sessionStats={{
                flightsDetected: sessionStats.flightsDetected,
                uniqueAircraft: sessionStats.uniqueAircraft.size,
                sessionDuration: getSessionDuration(),
              }}
              showScanScreen={flights.length === 0}
            />
            {flights.length > 1 && (
              <div className="display-controls">
                <p className="display-indicator">
                  Showing flight {currentFlightIndex + 1} of {flights.length}
                </p>
              </div>
            )}
          </div>

          <div className="board-section">
            <FlightBoard flights={allTrackedFlights} currentFlights={flights} />
          </div>
        </>
      )}
    </div>
  );
}
