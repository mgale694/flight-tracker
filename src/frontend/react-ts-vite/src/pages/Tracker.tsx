import React, { useState, useEffect } from 'react';
import { FlightTrackerAPI } from '../api';
import { WaveshareDisplay } from '../components/WaveshareDisplay';
import { FlightBoard } from '../components/FlightBoard';
import type { FlightData } from '../types';

export const Tracker: React.FC = () => {
  const [flights, setFlights] = useState<FlightData[]>([]);
  const [currentFlight, setCurrentFlight] = useState<FlightData | null>(null);
  const [stats, setStats] = useState({
    flights_count: 0,
    elapsed_str: '00:00:00'
  });
  const [timestamp, setTimestamp] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [isBooting, setIsBooting] = useState(true);
  const [bootData, setBootData] = useState<{
    face: string;
    phrase: string;
    message: string;
  } | null>(null);
  const [flightRotationIndex, setFlightRotationIndex] = useState(0);

  // Initialize component
  useEffect(() => {
    initializeTracker();
    
    const interval = setInterval(() => {
      fetchData();
    }, 5000); // Poll every 5 seconds

    const rotationInterval = setInterval(() => {
      rotateCurrentFlight();
    }, 10000); // Rotate display every 10 seconds

    return () => {
      clearInterval(interval);
      clearInterval(rotationInterval);
    };
  }, []);

  const initializeTracker = async () => {
    try {
      // Reset session timer on initialization
      sessionStorage.setItem('flight-tracker-session-start', Date.now().toString());
      
      // Show boot sequence
      const bootResponse = await FlightTrackerAPI.getBootData();
      setBootData(bootResponse);
      setIsBooting(true);

      // Simulate boot time
      setTimeout(() => {
        setIsBooting(false);
        fetchData();
      }, 3000);

    } catch (error) {
      console.error('Failed to initialize tracker:', error);
      setIsBooting(false);
      setIsConnected(false);
      setIsLoading(false);
    }
  };

  const fetchData = async () => {
    try {
      const response = await FlightTrackerAPI.getFlights();
      
      setFlights(response.flights);
      
      // Calculate elapsed time from start of session (more realistic)
      const sessionStart = sessionStorage.getItem('flight-tracker-session-start');
      const startTime = sessionStart ? parseInt(sessionStart) : Date.now();
      if (!sessionStart) {
        sessionStorage.setItem('flight-tracker-session-start', startTime.toString());
      }
      
      setStats({
        flights_count: response.flights.length,
        elapsed_str: formatElapsedTime(Date.now() - startTime)
      });
      setTimestamp(new Date().toISOString());
      setIsConnected(true);
      setIsLoading(false);

      // Update current flight if flights available
      if (response.flights.length > 0 && flightRotationIndex < response.flights.length) {
        setCurrentFlight(response.flights[flightRotationIndex]);
      } else if (response.flights.length === 0) {
        setCurrentFlight(null);
        setFlightRotationIndex(0);
      }

    } catch (error) {
      console.error('Failed to fetch flight data:', error);
      setIsConnected(false);
    }
  };

  const rotateCurrentFlight = () => {
    if (flights.length > 0) {
      setFlightRotationIndex(prev => {
        const newIndex = (prev + 1) % flights.length;
        setCurrentFlight(flights[newIndex]);
        return newIndex;
      });
    }
  };

  const formatElapsedTime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="tracker-page">
      <div className="tracker-container">
        {/* Left Column - Waveshare Display Simulation */}
        <div className="tracker-display-column">
          <div className="display-header">
            <h2>Raspberry Pi Display</h2>
            <div className="display-status">
              <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
                {isConnected ? '🟢' : '🔴'}
              </span>
              <span className="status-text">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
          
          <WaveshareDisplay
            flight={currentFlight}
            stats={stats}
            timestamp={timestamp}
            isBooting={isBooting}
            bootData={bootData || undefined}
          />
          
          <div className="display-info">
            <p className="display-description">
              Simulates the Waveshare 2.13" e-ink display on the Raspberry Pi.
              Shows current tracked flight information, rotating every 10 seconds.
            </p>
            {flights.length > 1 && (
              <div className="rotation-indicator">
                Flight {flightRotationIndex + 1} of {flights.length}
                <div className="rotation-dots">
                  {flights.map((_, index) => (
                    <span
                      key={index}
                      className={`dot ${index === flightRotationIndex ? 'active' : ''}`}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Flight Board */}
        <div className="tracker-board-column">
          <div className="board-header">
            <h2>Flight Board</h2>
            <div className="board-stats">
              <span className="flight-count">
                {flights.length} {flights.length === 1 ? 'Flight' : 'Flights'} Detected
              </span>
            </div>
          </div>
          
          <FlightBoard currentFlights={flights} />
          
          <div className="board-info">
            <p className="board-description">
              Rolling list of detected flights, similar to an airport departure board.
              Shows recent and current flights in your tracking area.
            </p>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="tracker-status-bar">
        <div className="status-item">
          <span className="label">Last Update:</span>
          <span className="value">{timestamp || 'Never'}</span>
        </div>
        <div className="status-item">
          <span className="label">Session Time:</span>
          <span className="value">{stats.elapsed_str}</span>
        </div>
        <div className="status-item">
          <span className="label">Total Flights:</span>
          <span className="value">{stats.flights_count}</span>
        </div>
        {isLoading && (
          <div className="status-item">
            <span className="loading-spinner">⟳</span>
            <span className="value">Loading...</span>
          </div>
        )}
      </div>
    </div>
  );
};
