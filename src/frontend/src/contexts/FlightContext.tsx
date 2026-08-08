/**
 * Flight Context - Global state management for flight tracking
 */

import { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { Flight } from '../types';
import { api } from '../api';
import { FlightContext } from './flight-context';

export function FlightProvider({ children }: { children: ReactNode }) {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [allTrackedFlights, setAllTrackedFlights] = useState<Flight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sessionStats, setSessionStats] = useState({
    flightsDetected: 0,
    uniqueAircraft: new Set<string>(),
    sessionStart: new Date().toISOString(),
  });

  // Fetch flights
  useEffect(() => {
    const fetchFlights = async () => {
      try {
        setError(null);
        const data = await api.getFlights();
        setFlights(data);
        
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

    // The web can update more often than e-paper, without hammering the API.
    const interval = setInterval(fetchFlights, 15000);

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
      }}
    >
      {children}
    </FlightContext.Provider>
  );
}
