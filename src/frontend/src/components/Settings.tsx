/**
 * Settings component for configuration management
 */

import { useState, useEffect } from 'react';
import type { ConfigUpdate } from '../types';
import { api } from '../api';
import DisplayFieldSelector from './DisplayFieldSelector';
import './Settings.css';

export default function Settings() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState<ConfigUpdate>({});

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getConfig();
      setFormData({
        address: data.main.address,
        search_radius_meters: data.main.search_radius_meters,
        max_flights: data.main.max_flights,
        max_elapsed_time: data.main.max_elapsed_time,
        display_hold_time: data.main.display_hold_time,
        display_fields: data.main.display_fields || ['FROM', 'AIRLINE', 'MODEL', 'REG', 'ROUTE'],
        bearing_degrees: data.viewing_zone?.bearing_degrees,
        field_of_view_degrees: data.viewing_zone?.field_of_view_degrees,
        min_distance_km: data.viewing_zone?.min_distance_km,
        max_distance_km: data.viewing_zone?.max_distance_km,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError(null);
      setSuccess(false);
      
      await api.updateConfig(formData);
      setSuccess(true);
      
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field: keyof ConfigUpdate, value: string | number | string[]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleClearDisplay = async () => {
    if (!window.confirm('Clear the e-ink display?')) {
      return;
    }
    
    try {
      setSaving(true);
      setError(null);
      const result = await api.clearDisplay();
      setSuccess(true);
      setError(result.status === 'error' ? result.message : null);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear display');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="settings-loading">
        <div className="loading"></div>
        <p>Loading configuration...</p>
      </div>
    );
  }

  return (
    <div className="settings">
      <h2>Window configuration</h2>
      
      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {success && (
        <div className="alert alert-success">
          <strong>Success!</strong> Configuration updated
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="settings-form">
        <div className="form-group">
          <label htmlFor="address">
            Window location
            <span className="label-hint">Your precise location stays in the product backend</span>
          </label>
          <input
            type="text"
            id="address"
            value={formData.address || ''}
            onChange={(e) => handleInputChange('address', e.target.value)}
            placeholder="e.g., San Francisco, CA"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="radius">
            Legacy nearby radius (metres)
            <span className="label-hint">Used until all live queries consume the viewing zone</span>
          </label>
          <input
            type="number"
            id="radius"
            value={formData.search_radius_meters || ''}
            onChange={(e) => handleInputChange('search_radius_meters', parseInt(e.target.value))}
            min="100"
            max="50000"
            step="100"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="maxFlights">
            Maximum Flights
            <span className="label-hint">1 - 100 flights</span>
          </label>
          <input
            type="number"
            id="maxFlights"
            value={formData.max_flights || ''}
            onChange={(e) => handleInputChange('max_flights', parseInt(e.target.value))}
            min="1"
            max="100"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="maxElapsed">
            Max Flight Age (seconds)
            <span className="label-hint">60 - 7200 seconds</span>
          </label>
          <input
            type="number"
            id="maxElapsed"
            value={formData.max_elapsed_time || ''}
            onChange={(e) => handleInputChange('max_elapsed_time', parseInt(e.target.value))}
            min="60"
            max="7200"
            step="60"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="displayHold">
            Display Hold Time (seconds)
            <span className="label-hint">How long to show last flight when none detected (5-300 seconds)</span>
          </label>
          <input
            type="number"
            id="displayHold"
            value={formData.display_hold_time || ''}
            onChange={(e) => handleInputChange('display_hold_time', parseInt(e.target.value))}
            min="5"
            max="300"
            step="5"
            required
          />
        </div>

        <div className="form-group">
          <label>
            E-ink Display Fields
            <span className="label-hint">Choose up to 5 fields • Drag to reorder</span>
          </label>
          <DisplayFieldSelector
            selectedFields={formData.display_fields || []}
            onChange={(fields) => handleInputChange('display_fields', fields)}
          />
        </div>
        
        <div className="form-actions">
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
          
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={loadConfig}
            disabled={saving}
          >
            Reset
          </button>
        </div>
      </form>
      
      <div className="system-controls">
        <h3>Display Controls</h3>
        <div className="control-buttons">
          <button 
            type="button" 
            className="btn btn-warning"
            onClick={handleClearDisplay}
            disabled={saving}
          >
            Clear display
          </button>
        </div>
      </div>
      
    </div>
  );
}
