import type { FlightData, SessionStats, BootData, Config } from './types';

const API_BASE = 'http://localhost:8000';

export class FlightTrackerAPI {
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

  static async getBootData(): Promise<BootData> {
    const response = await fetch(`${API_BASE}/boot`);
    if (!response.ok) throw new Error('Failed to fetch boot data');
    return response.json();
  }

  static async getFlights(): Promise<{ flights: FlightData[]; stats: SessionStats | null }> {
    const response = await fetch(`${API_BASE}/flights`);
    if (!response.ok) throw new Error('Failed to fetch flights');
    return response.json();
  }

  static async startSession(): Promise<void> {
    const response = await fetch(`${API_BASE}/session/start`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to start session');
  }

  static async stopSession(): Promise<void> {
    const response = await fetch(`${API_BASE}/session/stop`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to stop session');
  }

  static async getSessionStatus(): Promise<{
    active: boolean;
    stats: SessionStats | null;
    should_continue: boolean;
  }> {
    const response = await fetch(`${API_BASE}/session/status`);
    if (!response.ok) throw new Error('Failed to fetch session status');
    return response.json();
  }

  static createWebSocket(): WebSocket {
    return new WebSocket(`ws://localhost:8000/ws`);
  }
}
