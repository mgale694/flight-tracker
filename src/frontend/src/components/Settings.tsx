/**
 * Settings component for configuration management
 */

import { useCallback, useEffect, useState } from 'react';
import type { ConfigUpdate, LocationPreview } from '../types';
import { api } from '../api';
import DisplayFieldSelector from './DisplayFieldSelector';
import ViewingZoneEditor from './ViewingZoneEditor';
import './Settings.css';

export default function Settings() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [locationPreview, setLocationPreview] = useState<LocationPreview | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [resolvingLocation, setResolvingLocation] = useState(false);

  const [formData, setFormData] = useState<ConfigUpdate>({});

  const resolveLocation = useCallback(async (address: string) => {
    setResolvingLocation(true);
    setLocationError(null);
    try {
      const preview = await api.previewLocation(address.trim());
      setLocationPreview(preview);
      return preview;
    } catch (locationFailure) {
      const message = locationFailure instanceof Error
        ? locationFailure.message
        : 'Could not resolve that location';
      setLocationError(message);
      throw locationFailure;
    } finally {
      setResolvingLocation(false);
    }
  }, []);

  const loadConfig = useCallback(async () => {
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
      try {
        await resolveLocation(data.main.address);
      } catch {
        // The form remains usable for correcting an address that cannot be resolved.
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  }, [resolveLocation]);

  useEffect(() => {
    void loadConfig();
  }, [loadConfig]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError(null);
      setSuccess(false);
      
      await resolveLocation(formData.address || '');
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

  const handleViewingDistanceChange = (value: number) => {
    setFormData(prev => ({
      ...prev,
      max_distance_km: value,
      search_radius_meters: value * 1000,
    }));
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
            Full window address
            <span className="label-hint">A house number and street gives a clearer origin than a postcode alone</span>
          </label>
          <div className="address-entry">
            <input
              type="text"
              id="address"
              autoComplete="street-address"
              value={formData.address || ''}
              onChange={(event) => {
                handleInputChange('address', event.target.value);
                setLocationPreview(null);
                setLocationError(null);
              }}
              onBlur={() => {
                if ((formData.address || '').trim().length >= 3) {
                  void resolveLocation(formData.address || '').catch(() => undefined);
                }
              }}
              placeholder="10 Downing Street, London, SW1A 2AA"
              required
            />
            <button
              type="button"
              className="btn btn-secondary"
              disabled={resolvingLocation || (formData.address || '').trim().length < 3}
              onClick={() => void resolveLocation(formData.address || '').catch(() => undefined)}
            >
              {resolvingLocation ? 'Finding address…' : 'Update map'}
            </button>
          </div>
          {locationError && <span className="location-error">{locationError}</span>}
        </div>
        
        <section className="viewing-settings">
          <div>
            <h3>Visible sky</h3>
            <p>Match the direction, angle, and clear distance from your window.</p>
          </div>
          <ViewingZoneEditor
            bearing={formData.bearing_degrees ?? 0}
            fieldOfView={formData.field_of_view_degrees ?? 80}
            maxDistance={formData.max_distance_km ?? 35}
            location={locationPreview}
            onBearingChange={(value) => handleInputChange('bearing_degrees', value)}
            onFieldOfViewChange={(value) => handleInputChange('field_of_view_degrees', value)}
            onMaxDistanceChange={handleViewingDistanceChange}
          />
        </section>
        
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
            <span className="label-hint">Choose up to five lines and set their order</span>
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
