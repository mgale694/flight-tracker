/**
 * TypeScript type definitions for the Flight Tracker application
 */

export interface Flight {
  id: string;
  callsign: string;
  registration: string;
  aircraft: string;
  airline: string;
  origin: string;
  destination: string;
  altitude: number;
  speed: number;
  heading: number;
  latitude: number;
  longitude: number;
  distance: number;
  timestamp: string;
}

export interface Config {
  main: {
    address: string;
    search_radius_meters: number;
    max_flights: number;
    max_elapsed_time: number;
  };
  logging?: {
    max_activities: number;
    categories: string[];
  };
}

export interface ConfigUpdate {
  address?: string;
  search_radius_meters?: number;
  max_flights?: number;
  max_elapsed_time?: number;
}

export interface Activity {
  timestamp: string;
  category: string;
  message: string;
  details?: Record<string, any>;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export interface APIResponse {
  name: string;
  version: string;
  status: string;
}

export type Theme = 'light' | 'dark' | 'auto';

export interface SessionStats {
  flightsDetected: number;
  uniqueAircraft: number;
  sessionStart: string;
  sessionDuration: string;
}
