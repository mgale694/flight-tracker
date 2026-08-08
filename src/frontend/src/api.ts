/**
 * API client for communicating with the Flight Tracker backend
 */

import type {
  Activity,
  Config,
  ConfigUpdate,
  Flight,
  LocationPreview,
  PairingStatus,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

interface APIErrorPayload {
  detail?: string;
}

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
        const payload: APIErrorPayload = await response
          .json()
          .catch(() => ({ detail: response.statusText }));
        throw new Error(payload.detail || `HTTP ${response.status}: ${response.statusText}`);
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
   * Get current flights in the configured area
   */
  async getFlights(): Promise<Flight[]> {
    return this.fetchJSON<Flight[]>('/api/flights');
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

  async previewLocation(address: string): Promise<LocationPreview> {
    const params = new URLSearchParams({ address });
    return this.fetchJSON<LocationPreview>(`/api/location-preview?${params.toString()}`);
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

  async getPairingStatus(deviceId: string): Promise<PairingStatus> {
    return this.fetchJSON<PairingStatus>(
      `/api/v1/devices/${encodeURIComponent(deviceId)}/pairing-status`,
    );
  }

  async pairDevice(deviceId: string, pairingCode: string): Promise<PairingStatus> {
    return this.fetchJSON<PairingStatus>(`/api/v1/devices/${encodeURIComponent(deviceId)}/pair`, {
      method: 'POST',
      body: JSON.stringify({ pairing_code: pairingCode }),
    });
  }
}

// Export singleton instance
export const api = new APIClient();

// Export class for testing
export default APIClient;
