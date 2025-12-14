/**
 * Activities page - Activity log viewer
 */

import { useState, useEffect } from 'react';
import { Activity } from '../types';
import { api } from '../api';
import './Activities.css';

const CATEGORY_COLORS: Record<string, string> = {
  SYSTEM: '#9c27b0',
  RADAR: '#2196f3',
  FLIGHT: '#4caf50',
  CONFIG: '#ff9800',
  ERROR: '#f44336',
  INFO: '#00bcd4',
};

export default function Activities() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchActivities = async () => {
    try {
      setError(null);
      const data = await api.getActivities(100, filter || undefined);
      setActivities(data);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch activities');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, [filter]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchActivities, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, filter]);

  const handleClearLogs = async () => {
    if (!confirm('Are you sure you want to clear all activity logs?')) {
      return;
    }

    try {
      await api.clearActivities();
      setActivities([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear activities');
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getCategoryColor = (category: string) => {
    return CATEGORY_COLORS[category] || '#757575';
  };

  return (
    <div className="activities-page">
      <div className="activities-header">
        <div>
          <h1>Activity Logs</h1>
          <p className="activities-subtitle">Real-time system activity monitoring</p>
        </div>
        
        <div className="activities-controls">
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <span>Auto-refresh</span>
          </label>
          
          <button 
            className="btn btn-secondary" 
            onClick={fetchActivities}
            disabled={loading}
          >
            🔄 Refresh
          </button>
          
          <button 
            className="btn btn-secondary" 
            onClick={handleClearLogs}
          >
            🗑️ Clear Logs
          </button>
        </div>
      </div>

      <div className="filter-section">
        <label htmlFor="category-filter">Filter by category:</label>
        <select
          id="category-filter"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="SYSTEM">SYSTEM</option>
          <option value="RADAR">RADAR</option>
          <option value="FLIGHT">FLIGHT</option>
          <option value="CONFIG">CONFIG</option>
          <option value="ERROR">ERROR</option>
          <option value="INFO">INFO</option>
        </select>
        
        {activities.length > 0 && (
          <span className="activity-count">
            {activities.length} {activities.length === 1 ? 'activity' : 'activities'}
          </span>
        )}
      </div>

      {loading && (
        <div className="activities-loading">
          <div className="loading"></div>
          <p>Loading activities...</p>
        </div>
      )}

      {error && (
        <div className="activities-error">
          <p>❌ {error}</p>
        </div>
      )}

      {!loading && !error && activities.length === 0 && (
        <div className="activities-empty">
          <p>No activities to display</p>
        </div>
      )}

      {!loading && !error && activities.length > 0 && (
        <div className="activities-list">
          {activities.map((activity, index) => (
            <div key={`${activity.timestamp}-${index}`} className="activity-item">
              <div className="activity-header-row">
                <span
                  className="activity-category"
                  style={{ backgroundColor: getCategoryColor(activity.category) }}
                >
                  {activity.category}
                </span>
                <span className="activity-timestamp">
                  {formatTimestamp(activity.timestamp)}
                </span>
              </div>
              
              <p className="activity-message">{activity.message}</p>
              
              {activity.details && (
                <details className="activity-details">
                  <summary>View details</summary>
                  <pre>{JSON.stringify(activity.details, null, 2)}</pre>
                </details>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
