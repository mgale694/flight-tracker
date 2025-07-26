import React, { useState, useEffect, useRef } from 'react';
import { BootScreen, FlightScreen } from '../components/Display';
import { FlightTrackerAPI } from '../api';
import type { BootData, FlightData, SessionStats, WebSocketMessage } from '../types';

export const Tracker: React.FC = () => {
  const [bootData, setBootData] = useState<BootData | null>(null);
  const [currentFlight, setCurrentFlight] = useState<FlightData | null>(null);
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [isBooting, setIsBooting] = useState(true);
  const [isTracking, setIsTracking] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [currentTime, setCurrentTime] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Update time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('en-GB', { hour12: false }));
    }, 1000);

    // Initial boot sequence
    initializeBoot();

    return () => {
      clearInterval(timeInterval);
      if (wsRef.current) {
        wsRef.current.close();
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
        setupWebSocket();
      }, 3000);
    } catch (error) {
      console.error('Error initializing boot:', error);
      addLog('Error during boot sequence');
    }
  };

  const setupWebSocket = () => {
    try {
      const ws = FlightTrackerAPI.createWebSocket();
      wsRef.current = ws;

      ws.onopen = () => {
        addLog('Connected to flight tracker');
      };

      ws.onmessage = (event) => {
        const message: WebSocketMessage = JSON.parse(event.data);
        handleWebSocketMessage(message);
      };

      ws.onclose = () => {
        addLog('Disconnected from flight tracker');
        // Attempt to reconnect after 5 seconds
        setTimeout(setupWebSocket, 5000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addLog('Connection error');
      };
    } catch (error) {
      console.error('Error setting up WebSocket:', error);
    }
  };

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'new_flight':
        if (message.flight && message.stats) {
          setCurrentFlight(message.flight);
          setStats(message.stats);
          addLog(`✈️ ${message.message || `New flight: ${message.flight.callsign}`}`);
        }
        break;
      case 'stats_update':
        if (message.stats) {
          setStats(message.stats);
        }
        break;
      case 'session_started':
        addLog(message.message || 'Session started');
        break;
      case 'session_stopped':
        setIsTracking(false);
        addLog(message.message || 'Session stopped');
        break;
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
    } catch (error) {
      console.error('Error stopping session:', error);
      addLog('Error stopping tracking session');
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
