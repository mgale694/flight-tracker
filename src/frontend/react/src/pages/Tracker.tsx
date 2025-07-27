import React, { useState, useEffect, useRef } from 'react';
import { BootScreen, FlightScreen } from '../components/Display';
import { FlightTrackerAPI } from '../api';
import type { FlightData } from '../types';

export const Tracker: React.FC = () => {
  const [currentFlight, setCurrentFlight] = useState<FlightData | null>(null);
  const [isBooting, setIsBooting] = useState(true);
  const [logs, setLogs] = useState<string[]>([]);
  const [currentTime, setCurrentTime] = useState('');
  const [location, setLocation] = useState('');
  const pollIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    // Update time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('en-GB', { hour12: false }));
    }, 1000);

    // Start the app
    initialize();

    return () => {
      clearInterval(timeInterval);
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const initialize = async () => {
    try {
      // Mock boot sequence
      const bootData = await FlightTrackerAPI.getBootData();
      addLog(bootData.message);
      
      // Short boot sequence
      setTimeout(() => {
        setIsBooting(false);
        addLog("Ready! Starting flight monitoring...");
        startPolling();
      }, 2000);
    } catch (error) {
      console.error('Error initializing:', error);
      addLog('Error during startup');
    }
  };

  const startPolling = () => {
    // Poll every 3 seconds
    pollIntervalRef.current = window.setInterval(async () => {
      try {
        const flightData = await FlightTrackerAPI.getFlights();
        
        // Update location
        setLocation(flightData.location);
        
        if (flightData.flights.length > 0) {
          const latestFlight = flightData.flights[0];
          
          // Check if this is a new flight
          if (!currentFlight || currentFlight.id !== latestFlight.id) {
            setCurrentFlight(latestFlight);
            addLog(`✈️ ${latestFlight.callsign} detected at ${latestFlight.altitude} ft`);
          }
        } else {
          // No flights
          if (currentFlight) {
            addLog("No flights in area");
            setCurrentFlight(null);
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
        addLog('Error fetching flight data');
      }
    }, 3000);
  };

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString('en-GB', { hour12: false });
    setLogs(prev => [...prev.slice(-9), `[${timestamp}] ${message}`]);
  };

  const triggerManualRefresh = async () => {
    try {
      const flightData = await FlightTrackerAPI.getFlights();
      addLog(`Manual refresh: ${flightData.flights.length} flights found`);
      
      if (flightData.flights.length > 0) {
        setCurrentFlight(flightData.flights[0]);
      }
    } catch (error) {
      addLog('Error during manual refresh');
    }
  };

  const renderDisplay = () => {
    if (isBooting) {
      return (
        <BootScreen
          face="(⌐■_■)"
          phrase="Flight Tracker starting..."
          timestamp={currentTime}
        />
      );
    }

    if (currentFlight) {
      // Create mock stats for display compatibility
      const mockStats = {
        flights_count: 1,
        elapsed_time: Math.floor(Date.now() / 1000),
        elapsed_str: new Date().toLocaleTimeString(),
        location_short: location || 'Unknown'
      };

      return (
        <FlightScreen
          flight={currentFlight}
          stats={mockStats}
          timestamp={currentTime}
        />
      );
    }

    // Scanning state
    return (
      <BootScreen
        face="(◔_◔)"
        phrase="Scanning for aircraft..."
        timestamp={currentTime}
      />
    );
  };

  return (
    <div className="tracker-container">
      <h1>Flight Tracker</h1>
      
      <div className="display-section">
        {renderDisplay()}
      </div>

      <div className="controls-section">
        <button 
          onClick={triggerManualRefresh} 
          className="control-button"
          disabled={isBooting}
        >
          Refresh Now
        </button>
        
        <div className="status-info">
          <div className="status-item">
            <strong>Location:</strong> {location || 'Loading...'}
          </div>
          <div className="status-item">
            <strong>Status:</strong> {isBooting ? 'Starting...' : 'Monitoring'}
          </div>
          <div className="status-item">
            <strong>Current Flight:</strong> {currentFlight ? currentFlight.callsign : 'None'}
          </div>
        </div>
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
