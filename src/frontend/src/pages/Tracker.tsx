/**
 * Tracker page - Main dashboard with display and flight board
 */

import { useState, useEffect } from 'react';
import type { Flight } from '../types';
import { api } from '../api';
import WaveshareDisplay from '../components/WaveshareDisplay';
import FlightBoard from '../components/FlightBoard';
import './Tracker.css';

export default function Tracker() {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [allTrackedFlights, setAllTrackedFlights] = useState<Flight[]>([]);
  const [currentFlightIndex, setCurrentFlightIndex] = useState(0);
  const [lastFlight, setLastFlight] = useState<Flight | null>(null);
  const [lastFlightTime, setLastFlightTime] = useState<number>(0);
  const [displayHoldTime, setDisplayHoldTime] = useState<number>(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sessionStats, setSessionStats] = useState({
    flightsDetected: 0,
    uniqueAircraft: new Set<string>(),
    sessionStart: new Date().toISOString(),
  });

  // Fetch display hold time from config
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const config = await api.getConfig();
        setDisplayHoldTime(config.main.display_hold_time || 30);
      } catch (err) {
        console.error('Failed to fetch config:', err);
      }
    };
    fetchConfig();
  }, []);

  //  Fetch flights
  useEffect(() => {
    const fetchFlights = async () => {
      try {
        setError(null);
        const data = await api.getFlights();
        setFlights(data);
        
        // If we have flights, update last flight and timestamp
        if (data.length > 0) {
          setLastFlight(data[0]);
          setLastFlightTime(Date.now());
        }
        
        // Add new flights to the tracked history (avoid duplicates by registration)
        setAllTrackedFlights(prev => {
          const existingIds = new Set(prev.map(f => f.registration));
          const newFlights = data.filter(f => !existingIds.has(f.registration));
          // Add new flights to the beginning (newest first)
          return [...newFlights, ...prev];
        });
        
        // Update session stats
        setSessionStats(prev => ({
          ...prev,
          flightsDetected: prev.flightsDetected + data.length,
          uniqueAircraft: new Set([...prev.uniqueAircraft, ...data.map(f => f.registration)]),
        }));
        
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch flights');
        setLoading(false);
      }
    };

    // Initial fetch
    fetchFlights();

    // Poll every 5 seconds
    const interval = setInterval(fetchFlights, 5000);

    return () => clearInterval(interval);
  }, []);

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
