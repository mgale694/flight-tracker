import type { FlightData, Config } from './types';

const API_BASE = 'http://localhost:8000';

export class FlightTrackerAPI {
  // Main endpoint - gets current flights (simplified)
  static async getFlights(): Promise<{ 
    flights: FlightData[]; 
    timestamp: number; 
    location: string; 
  }> {
    const response = await fetch(`${API_BASE}/flights`);
    if (!response.ok) throw new Error('Failed to fetch flights');
    return response.json();
  }

  // Config management
  static async getConfig(): Promise<Config> {
    const response = await fetch(`${API_BASE}/config`);
    if (!response.ok) throw new Error('Failed to fetch config');
    const data = await response.json();
    return data.main;
  }

  static async updateConfig(config: Config): Promise<void> {
    const response = await fetch(`${API_BASE}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to update config');
  }

  // Health check
  static async getHealth(): Promise<{
    status: string;
    timestamp: number;
    tracker_initialized: boolean;
  }> {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Failed to fetch health status');
    return response.json();
  }

  // Mock boot data for compatibility (since simplified backend doesn't have this)
  static async getBootData(): Promise<{ face: string; phrase: string; message: string }> {
    const faces = ["(⌐■_■)", "(╯°□°）╯", "ಠ_ಠ", "(◕‿◕)", "¯\\_(ツ)_/¯"];
    const phrases = [
      "Booting up flight tracker...",
      "Scanning the skies...", 
      "Ready for takeoff!",
      "Aircraft detection online",
      "Flight radar activated"
    ];
    
    return {
      face: faces[Math.floor(Math.random() * faces.length)],
      phrase: phrases[Math.floor(Math.random() * phrases.length)],
      message: "Flight Tracker initialized"
    };
  }
}
