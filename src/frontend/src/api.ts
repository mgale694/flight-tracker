/**
 * API client for communicating with the Flight Tracker backend
 */

import type { Flight, Config, ConfigUpdate, Activity, HealthResponse, APIResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Generic fetch wrapper with error handling
   */
  private async fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unknown error occurred');
    }
  }

  /**
   * Get API information
   */
  async getAPIInfo(): Promise<APIResponse> {
    return this.fetchJSON<APIResponse>('/');
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthResponse> {
    return this.fetchJSON<HealthResponse>('/api/health');
  }

  /**
   * Get current flights in the configured area
   */
  async getFlights(): Promise<Flight[]> {
    return this.fetchJSON<Flight[]>('/api/flights');
  }

  /**
   * Get detailed information about a specific flight
   */
  async getFlightDetails(flightId: string): Promise<any> {
    return this.fetchJSON(`/api/flight/${flightId}`);
  }

  /**
   * Get current configuration
   */
  async getConfig(): Promise<Config> {
    return this.fetchJSON<Config>('/api/config');
  }

  /**
   * Update configuration
   */
  async updateConfig(config: ConfigUpdate): Promise<Config> {
    return this.fetchJSON<Config>('/api/config', {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  /**
   * Get activity logs
   */
  async getActivities(limit?: number, category?: string): Promise<Activity[]> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (category) params.append('category', category);
    
    const query = params.toString();
    const endpoint = `/api/activities${query ? `?${query}` : ''}`;
    
    return this.fetchJSON<Activity[]>(endpoint);
  }

  /**
   * Clear activity logs
   */
  async clearActivities(): Promise<{ message: string }> {
    return this.fetchJSON('/api/activities', {
      method: 'DELETE',
    });
  }

  /**
   * Clear the e-ink display
   */
  async clearDisplay(): Promise<{ status: string; message: string }> {
    return this.fetchJSON('/api/system/clear-display', {
      method: 'POST',
    });
  }

  /**
   * Shutdown the flight tracker system
   */
  async shutdownSystem(): Promise<{ status: string; message: string }> {
    return this.fetchJSON('/api/system/shutdown', {
      method: 'POST',
    });
  }
}

// Export singleton instance
export const api = new APIClient();

// Export class for testing
export default APIClient;
