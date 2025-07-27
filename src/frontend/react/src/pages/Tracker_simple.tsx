import React, { useState, useEffect, useRef } from 'react';
import { BootScreen, FlightScreen } from '../components/Display';
import { FlightTrackerAPI } from '../api';
import type { BootData, FlightData, SessionStats } from '../types';

export const Tracker: React.FC = () => {
  const [bootData, setBootData] = useState<BootData | null>(null);
  const [currentFlight, setCurrentFlight] = useState<FlightData | null>(null);
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [isBooting, setIsBooting] = useState(true);
  const [isTracking, setIsTracking] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [currentTime, setCurrentTime] = useState('');
  const pollIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    // Update time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('en-GB', { hour12: false }));
    }, 1000);

    // Initial boot sequence
    initializeBoot();

    return () => {
      clearInterval(timeInterval);
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const initializeBoot = async () => {
    try {
      const boot = await FlightTrackerAPI.getBootData();
      setBootData(boot);
      addLog(boot.message);
      
      // Boot sequence duration (like the original)
      setTimeout(() => {
        setIsBooting(false);
        addLog("Boot sequence complete!");
        startPolling();
      }, 3000);
    } catch (error) {
      console.error('Error initializing boot:', error);
      addLog('Error during boot sequence');
    }
  };

  const startPolling = () => {
    addLog('Starting flight monitoring...');
    
    // Poll every 3 seconds
    pollIntervalRef.current = window.setInterval(async () => {
      try {
        const flightData = await FlightTrackerAPI.getFlights();
        
        if (flightData.flights.length > 0) {
          const latestFlight = flightData.flights[0]; // Get the first flight
          
          // Check if this is a new flight (different from current)
          if (!currentFlight || currentFlight.id !== latestFlight.id) {
            setCurrentFlight(latestFlight);
            addLog(`✈️ New flight detected: ${latestFlight.callsign}`);
          }
        } else {
          // No flights, clear current flight after a delay
          if (currentFlight) {
            setTimeout(() => setCurrentFlight(null), 5000);
          }
        }
        
        setStats(flightData.stats);
      } catch (error) {
        console.error('Polling error:', error);
        addLog('Error fetching flight data');
      }
    }, 3000);
  };

  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString('en-GB', { hour12: false });
    setLogs(prev => [...prev.slice(-19), `[${timestamp}] ${message}`]);
  };

  const startTracking = async () => {
    try {
      await FlightTrackerAPI.startSession();
      setIsTracking(true);
      setCurrentFlight(null);
      setStats(null);
      addLog('Flight tracking session started');
    } catch (error) {
      console.error('Error starting session:', error);
      addLog('Error starting tracking session');
    }
  };

  const stopTracking = async () => {
    try {
      await FlightTrackerAPI.stopSession();
      setIsTracking(false);
      addLog('Flight tracking session stopped');
      stopPolling();
    } catch (error) {
      console.error('Error stopping session:', error);
      addLog('Error stopping tracking session');
    }
  };

  const triggerDemoFlight = async () => {
    try {
      const response = await fetch('http://localhost:8000/demo/flight');
      const data = await response.json();
      if (data.flight && data.stats) {
        setCurrentFlight(data.flight);
        setStats(data.stats);
        addLog(`✈️ Demo flight: ${data.flight.callsign}`);
      }
    } catch (error) {
      console.error('Error triggering demo flight:', error);
      addLog('Error triggering demo flight');
    }
  };

  const renderDisplay = () => {
    if (isBooting && bootData) {
      return (
        <BootScreen
          face={bootData.face}
          phrase={bootData.phrase}
          timestamp={currentTime}
        />
      );
    }

    if (currentFlight && stats) {
      return (
        <FlightScreen
          flight={currentFlight}
          stats={stats}
          timestamp={currentTime}
        />
      );
    }

    // Idle/waiting screen
    return (
      <BootScreen
        face="(⚆_⚆)"
        phrase="Scanning for aircraft..."
        timestamp={currentTime}
      />
    );
  };

  return (
    <div className="tracker-container">
      <h1>Flight Tracker Display</h1>
      
      <div className="display-section">
        {renderDisplay()}
      </div>

      <div className="controls-section">
        <div className="tracking-controls">
          {!isTracking ? (
            <button 
              onClick={startTracking} 
              className="control-button start-button"
              disabled={isBooting}
            >
              Start Tracking
            </button>
          ) : (
            <button 
              onClick={stopTracking} 
              className="control-button stop-button"
            >
              Stop Tracking
            </button>
          )}
        </div>

        <div className="demo-controls">
          <button 
            onClick={triggerDemoFlight} 
            className="control-button demo-button"
            disabled={isBooting}
          >
            Trigger Demo Flight
          </button>
        </div>

        {stats && (
          <div className="status-info">
            <div className="status-item">
              <strong>Flights Detected:</strong> {stats.flights_count}
            </div>
            <div className="status-item">
              <strong>Session Time:</strong> {stats.elapsed_str}
            </div>
            <div className="status-item">
              <strong>Location:</strong> {stats.location_short}
            </div>
          </div>
        )}
      </div>

      <div className="logs-section">
        <h3>Activity Log</h3>
        <div className="logs-container">
          {logs.map((log, index) => (
            <div key={index} className="log-entry">
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
