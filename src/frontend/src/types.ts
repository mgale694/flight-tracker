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
  origin_name?: string;
  destination_name?: string;
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
    display_hold_time: number;
    display_fields?: string[];
  };
  logging?: {
    max_activities: number;
    categories: string[];
  };
  viewing_zone?: {
    bearing_degrees: number;
    field_of_view_degrees: number;
    min_distance_km: number;
    max_distance_km: number;
    min_altitude_ft?: number;
    max_altitude_ft?: number;
  };
  device?: {
    public_id: string;
    paired: boolean;
    setup_url: string;
  };
}

export interface ConfigUpdate {
  address?: string;
  search_radius_meters?: number;
  max_flights?: number;
  max_elapsed_time?: number;
  display_hold_time?: number;
  display_fields?: string[];
  bearing_degrees?: number;
  field_of_view_degrees?: number;
  min_distance_km?: number;
  max_distance_km?: number;
  min_altitude_ft?: number;
  max_altitude_ft?: number;
}

export interface Activity {
  timestamp: string;
  category: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface PairingStatus {
  device_id: string;
  paired: boolean;
  setup_url: string;
  authentication_mode: 'development' | 'production';
}

export type { Theme } from './theme';
