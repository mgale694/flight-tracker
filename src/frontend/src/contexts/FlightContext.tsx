/**
 * Flight Context - Global state management for flight tracking
 */

import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { Flight } from '../types';
import { api } from '../api';

interface FlightContextType {
  flights: Flight[];
  allTrackedFlights: Flight[];
  sessionStats: {
    flightsDetected: number;
    uniqueAircraft: Set<string>;
    sessionStart: string;
  };
  loading: boolean;
  error: string | null;
  displayHoldTime: number;
  lastFlight: Flight | null;
  lastFlightTime: number;
}

const FlightContext = createContext<FlightContextType | undefined>(undefined);

export function FlightProvider({ children }: { children: ReactNode }) {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [allTrackedFlights, setAllTrackedFlights] = useState<Flight[]>([]);
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

  // Fetch flights
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

  return (
    <FlightContext.Provider
      value={{
        flights,
        allTrackedFlights,
        sessionStats,
        loading,
        error,
        displayHoldTime,
        lastFlight,
        lastFlightTime,
      }}
    >
      {children}
    </FlightContext.Provider>
  );
}

export function useFlights() {
  const context = useContext(FlightContext);
  if (context === undefined) {
    throw new Error('useFlights must be used within a FlightProvider');
  }
  return context;
}
