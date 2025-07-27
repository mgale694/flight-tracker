import React, { useState, useEffect, useRef } from 'react';
import { FlightTrackerAPI } from '../api';

interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error' | 'debug' | 'success';
  message: string;
  category?: string;
}

const LOG_STORAGE_KEY = 'flight_tracker_logs';
const MAX_LOGS = 500;

export const Activities: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [logFilter, setLogFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const pollIntervalRef = useRef<number | null>(null);

  // Load logs from localStorage and backend on mount
  useEffect(() => {
    loadStoredLogs();
    loadBackendLogs();
  }, []);

  const loadStoredLogs = () => {
    try {
      const savedLogs = localStorage.getItem(LOG_STORAGE_KEY);
      if (savedLogs) {
        const parsedLogs = JSON.parse(savedLogs).map((log: any) => ({
          ...log,
          timestamp: new Date(log.timestamp)
        }));
        setLogs(parsedLogs);
      }
    } catch (error) {
      console.error('Failed to load logs from localStorage:', error);
    }
  };

  const loadBackendLogs = async () => {
    try {
      const response = await FlightTrackerAPI.getActivityLogs();
      const backendLogs: LogEntry[] = response.logs.map(log => ({
        id: `backend-${log.id}`, // Prefix to avoid ID conflicts with frontend logs
        timestamp: new Date(log.timestamp),
        level: log.level as LogEntry['level'],
        message: log.message,
        category: log.category
      }));
      
      // Merge backend logs with existing logs, avoiding duplicates
      setLogs(prevLogs => {
        const existingIds = new Set(prevLogs.map(log => log.id));
        const newLogs = backendLogs.filter(log => !existingIds.has(log.id));
        
        // Combine and sort by timestamp
        const combined = [...prevLogs, ...newLogs].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
        return combined.slice(0, MAX_LOGS);
      });
      
      if (backendLogs.length > 0) {
        addLog('success', `Loaded ${backendLogs.length} logs from backend`, 'FRONTEND');
      }
    } catch (error) {
      addLog('warning', 'Could not load backend logs: ' + (error as Error).message, 'FRONTEND');
    }
  };

  // Save logs to localStorage when component unmounts
  useEffect(() => {
    return () => {
      try {
        const logsToStore = logs.map(log => ({
          ...log,
          timestamp: log.timestamp.toISOString()
        }));
        localStorage.setItem(LOG_STORAGE_KEY, JSON.stringify(logsToStore));
      } catch (error) {
        console.error('Failed to save logs to localStorage:', error);
      }
    };
  }, [logs]);

  // Filter logs based on level and search term
  useEffect(() => {
    let filtered = logs;
    
    if (logFilter !== 'all') {
      filtered = filtered.filter(log => log.level === logFilter);
    }
    
    if (searchTerm.trim()) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(search) ||
        log.category?.toLowerCase().includes(search)
      );
    }
    
    setFilteredLogs(filtered);
  }, [logs, logFilter, searchTerm]);

  useEffect(() => {
    // Start monitoring activities
    startActivityMonitoring();

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const addLog = (level: LogEntry['level'], message: string, category?: string) => {
    const newLog: LogEntry = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      level,
      message,
      category
    };
    
    setLogs(prev => {
      const updated = [newLog, ...prev];
      return updated.slice(0, MAX_LOGS); // Keep only the most recent logs
    });
  };

  const startActivityMonitoring = async () => {
    addLog('info', 'Flight tracker activity monitor started', 'FRONTEND');
    
    // Check backend health first
    try {
      await FlightTrackerAPI.getHealth();
      setIsConnected(true);
      addLog('success', 'Successfully connected to backend server', 'CONNECTION');
    } catch (error) {
      setIsConnected(false);
      addLog('error', 'Failed to connect to backend server', 'CONNECTION');
    }

    // Start polling for activities
    pollIntervalRef.current = setInterval(async () => {
      try {
        const response = await FlightTrackerAPI.getFlights();
        const flightCount = response.flights.length;
        
        // Only log frontend flight detection occasionally to avoid spam
        if (flightCount > 0) {
          addLog('debug', `Frontend detected ${flightCount} active flights`, 'FRONTEND');
        }
        
        if (!isConnected) {
          setIsConnected(true);
          addLog('success', 'Backend connection restored', 'CONNECTION');
        }
        
        // Refresh backend logs on every poll to catch API calls immediately
        loadBackendLogs();
      } catch (error) {
        if (isConnected) {
          setIsConnected(false);
          addLog('warning', 'Lost connection to backend server', 'CONNECTION');
        }
      }
    }, 5000); // Poll every 5 seconds for faster log updates
  };

  const clearLogs = async () => {
    try {
      // Clear backend logs first
      await FlightTrackerAPI.clearActivityLogs();
      addLog('success', 'Backend logs cleared successfully', 'FRONTEND');
    } catch (error) {
      addLog('warning', 'Failed to clear backend logs: ' + (error as Error).message, 'FRONTEND');
    }
    
    // Clear frontend logs
    setLogs([]);
    localStorage.removeItem(LOG_STORAGE_KEY);
    addLog('info', 'All activity logs cleared by user', 'FRONTEND');
  };

  const refreshLogs = async () => {
    addLog('info', 'Refreshing logs from backend...', 'FRONTEND');
    await loadBackendLogs();
  };

  const exportLogs = () => {
    const logData = filteredLogs.map(log => 
      `[${log.timestamp.toISOString()}] [${log.level.toUpperCase()}] ${log.category ? `[${log.category}] ` : ''}${log.message}`
    ).join('\n');
    
    const blob = new Blob([logData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `flight-tracker-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    addLog('info', 'Activity logs exported to file', 'SYSTEM');
  };

  const getLogIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'info': return 'ℹ️';
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      case 'debug': return '🔍';
      default: return '📝';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-GB', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="activities-page">
      <div className="activities-header">
        <div className="header-left">
          <h1>🖥️ Activity Console</h1>
          <div className="connection-status">
            <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
            <span className="status-text">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        
        <div className="header-controls">
          <div className="log-stats">
            <span className="stat-item">
              <span className="stat-label">Total:</span>
              <span className="stat-value">{logs.length}</span>
            </span>
            <span className="stat-item">
              <span className="stat-label">Filtered:</span>
              <span className="stat-value">{filteredLogs.length}</span>
            </span>
          </div>
          
          <button onClick={refreshLogs} className="btn btn-primary" title="Refresh backend logs">
            🔄 Refresh
          </button>
          <button onClick={exportLogs} className="btn btn-secondary" title="Export logs">
            📄 Export
          </button>
          <button onClick={clearLogs} className="btn btn-danger" title="Clear all logs">
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="console-controls">
        <div className="filter-controls">
          <select 
            value={logFilter} 
            onChange={(e) => setLogFilter(e.target.value)}
            className="log-filter-select"
          >
            <option value="all">All Levels</option>
            <option value="info">Info</option>
            <option value="success">Success</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="debug">Debug</option>
          </select>
          
          <input
            type="text"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="log-search-input"
          />
        </div>
      </div>

      <div className="console-container">
        <div className="console-header">
          <span className="console-title">Flight Tracker Console v1.0</span>
          <span className="console-info">
            {filteredLogs.length} entries | Last update: {new Date().toLocaleTimeString()}
          </span>
        </div>
        
        <div className="console-content">
          {filteredLogs.length === 0 ? (
            <div className="console-empty">
              <p>No log entries match current filter criteria.</p>
              {logs.length === 0 && <p>Starting activity monitoring...</p>}
            </div>
          ) : (
            filteredLogs.map((log) => (
              <div key={log.id} className={`console-line log-${log.level}`}>
                <span className="log-timestamp">{formatTimestamp(log.timestamp)}</span>
                <span className="log-level">
                  <span className="log-icon">{getLogIcon(log.level)}</span>
                  {log.level.toUpperCase()}
                </span>
                {log.category && <span className="log-category">[{log.category}]</span>}
                <span className="log-message">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
