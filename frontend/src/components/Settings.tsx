import React, { useState, useEffect } from 'react';
import type { Config } from '../types';
import { FlightTrackerAPI } from '../api';

export const Settings: React.FC = () => {
  const [config, setConfig] = useState<Config>({
    address: '',
    search_radius_meters: 3000,
    max_flights: 20,
    max_elapsed_time: 1800,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const currentConfig = await FlightTrackerAPI.getConfig();
      setConfig(currentConfig);
    } catch (error) {
      console.error('Error loading config:', error);
      setMessage('Error loading configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    
    try {
      await FlightTrackerAPI.updateConfig(config);
      setMessage('Configuration saved successfully!');
    } catch (error) {
      console.error('Error saving config:', error);
      setMessage('Error saving configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof Config, value: string | number) => {
    setConfig(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  if (loading) {
    return (
      <div className="settings-container">
        <div className="loading">Loading configuration...</div>
      </div>
    );
  }

  return (
    <div className="settings-container">
      <h1>Flight Tracker Settings</h1>
      
      <form onSubmit={handleSave} className="settings-form">
        <div className="form-group">
          <label htmlFor="address">Address:</label>
          <input
            type="text"
            id="address"
            value={config.address}
            onChange={(e) => handleChange('address', e.target.value)}
            placeholder="31 Maltings Place, Fulham, London, SW62BU"
            required
          />
          <small>The address to center flight tracking around</small>
        </div>

        <div className="form-group">
          <label htmlFor="radius">Search Radius (meters):</label>
          <input
            type="number"
            id="radius"
            value={config.search_radius_meters}
            onChange={(e) => handleChange('search_radius_meters', parseInt(e.target.value) || 3000)}
            min="1000"
            max="10000"
            step="500"
          />
          <small>Radius in meters to search for flights around the address</small>
        </div>

        <div className="form-group">
          <label htmlFor="maxFlights">Max Flights:</label>
          <input
            type="number"
            id="maxFlights"
            value={config.max_flights}
            onChange={(e) => handleChange('max_flights', parseInt(e.target.value) || 20)}
            min="1"
            max="100"
          />
          <small>Maximum number of flights to track in a session</small>
        </div>

        <div className="form-group">
          <label htmlFor="maxTime">Max Session Time (seconds):</label>
          <input
            type="number"
            id="maxTime"
            value={config.max_elapsed_time}
            onChange={(e) => handleChange('max_elapsed_time', parseInt(e.target.value) || 1800)}
            min="300"
            max="7200"
            step="300"
          />
          <small>Maximum session duration in seconds (default: 1800 = 30 minutes)</small>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={saving} className="save-button">
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>

        {message && (
          <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
      </form>
    </div>
  );
};
