import { createContext, useContext } from 'react';
import type { Flight } from '../types';

export interface FlightContextValue {
  flights: Flight[];
  allTrackedFlights: Flight[];
  sessionStats: {
    flightsDetected: number;
    uniqueAircraft: Set<string>;
    sessionStart: string;
  };
  loading: boolean;
  error: string | null;
}

export const FlightContext = createContext<FlightContextValue | undefined>(undefined);

export function useFlights(): FlightContextValue {
  const context = useContext(FlightContext);
  if (context === undefined) {
    throw new Error('useFlights must be used within a FlightProvider');
  }
  return context;
}
