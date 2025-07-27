import React, { useState, useEffect, useRef } from 'react';
import { FlightTrackerAPI } from '../api';

export const Activities: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const pollIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    // Start monitoring activities
    startActivityMonitoring();

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString('en-GB', { hour12: false });
    const logEntry = `[${timestamp}] ${message}`;
    setLogs(prev => [logEntry, ...prev].slice(0, 100)); // Keep last 100 logs
  };

  const startActivityMonitoring = async () => {
    addLog('Activity monitor started');
    
    // Check backend health first
    try {
      await FlightTrackerAPI.getHealth();
      setIsConnected(true);
      addLog('✅ Connected to backend');
    } catch (error) {
      setIsConnected(false);
      addLog('❌ Backend connection failed');
    }

    // Start polling for activities
    pollIntervalRef.current = setInterval(async () => {
      try {
        const response = await FlightTrackerAPI.getFlights();
        const flightCount = response.flights.length;
        
        if (flightCount > 0) {
          addLog(`📡 ${flightCount} flights detected`);
          
          // Log individual flights
          response.flights.forEach((flight, index) => {
            if (index < 3) { // Only log first 3 to avoid spam
              addLog(`✈️ ${flight.callsign || 'N/A'} - ${flight.altitude || 'N/A'}ft`);
            }
          });
          
          if (flightCount > 3) {
            addLog(`... and ${flightCount - 3} more flights`);
          }
        } else {
          addLog('🔍 Scanning for flights...');
        }
        
        if (!isConnected) {
          setIsConnected(true);
          addLog('✅ Backend reconnected');
        }
      } catch (error) {
        if (isConnected) {
          setIsConnected(false);
          addLog('❌ Lost connection to backend');
        }
      }
    }, 5000); // Poll every 5 seconds for activities
  };

  const clearLogs = () => {
    setLogs([]);
    addLog('Activity log cleared');
  };

  return (
    <div className="activities-container">
      <div className="activities-header">
        <h1>Flight Tracker Activity Log</h1>
        <div className="activities-controls">
          <div className="connection-status">
            <span className={`status-indicator ${isConnected ? 'online' : 'offline'}`}></span>
            <span className="status-text">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <button onClick={clearLogs} className="btn btn-secondary">
            Clear Log
          </button>
        </div>
      </div>

      <div className="activities-content">
        <div className="log-container">
          <div className="log-header">
            <h3>Real-time Activity Feed</h3>
            <span className="log-count">{logs.length} entries</span>
          </div>
          
          <div className="log-entries">
            {logs.length === 0 ? (
              <div className="log-empty">
                <p>No activity logged yet. Starting monitoring...</p>
              </div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="log-entry">
                  <span className="log-text">{log}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="activity-stats">
          <h3>Statistics</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total Entries</span>
              <span className="stat-value">{logs.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Status</span>
              <span className={`stat-value ${isConnected ? 'text-success' : 'text-danger'}`}>
                {isConnected ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Update Interval</span>
              <span className="stat-value">5 seconds</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
