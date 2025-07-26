export interface FlightData {
  callsign: string;
  id: string;
  latitude: number;
  longitude: number;
  altitude: string;
  ground_speed: string;
  origin_airport_name: string;
  destination_airport_name: string;
  origin_airport_iata: string;
  destination_airport_iata: string;
  airline_name: string;
  aircraft_model: string;
  registration: string;
}

export interface SessionStats {
  flights_count: number;
  elapsed_time: number;
  elapsed_str: string;
  location_short: string;
}

export interface BootData {
  face: string;
  phrase: string;
  timestamp: string;
  message: string;
}

export interface Config {
  address: string;
  search_radius_meters: number;
  max_flights: number;
  max_elapsed_time: number;
}

export interface WebSocketMessage {
  type: 'new_flight' | 'session_started' | 'session_stopped' | 'stats_update';
  flight?: FlightData;
  stats?: SessionStats;
  message?: string;
  timestamp: string;
}
