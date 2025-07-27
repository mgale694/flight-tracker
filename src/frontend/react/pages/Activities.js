function Activities() {
  const [logs, setLogs] = React.useState([]);
  const [filteredLogs, setFilteredLogs] = React.useState([]);
  const [logFilter, setLogFilter] = React.useState('all');
  const [searchTerm, setSearchTerm] = React.useState('');
  const [isConnected, setIsConnected] = React.useState(false);
  const pollIntervalRef = React.useRef(null);

  const LOG_STORAGE_KEY = 'flight_tracker_logs';
  const MAX_LOGS = 500;

  // Load logs from localStorage and backend on mount
  React.useEffect(() => {
    loadStoredLogs();
    loadBackendLogs();
  }, []);

  const loadStoredLogs = () => {
    try {
      const savedLogs = localStorage.getItem(LOG_STORAGE_KEY);
      if (savedLogs) {
        const parsedLogs = JSON.parse(savedLogs).map((log) => ({
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
      const response = await window.FlightTrackerAPI.getActivityLogs();
      const backendLogs = response.logs.map(log => ({
        id: `backend-${log.id}`, // Prefix to avoid ID conflicts with frontend logs
        timestamp: new Date(log.timestamp),
        level: log.level,
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
      addLog('warning', 'Could not load backend logs: ' + error.message, 'FRONTEND');
    }
  };

  // Save logs to localStorage when component unmounts
  React.useEffect(() => {
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
  React.useEffect(() => {
    let filtered = logs;
    
    if (logFilter !== 'all') {
      filtered = filtered.filter(log => log.level === logFilter);
    }
    
    if (searchTerm.trim()) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(search) ||
        (log.category && log.category.toLowerCase().includes(search))
      );
    }
    
    setFilteredLogs(filtered);
  }, [logs, logFilter, searchTerm]);

  React.useEffect(() => {
    // Start monitoring activities
    startActivityMonitoring();

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const addLog = (level, message, category) => {
    const newLog = {
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
      await window.FlightTrackerAPI.getHealth();
      setIsConnected(true);
      addLog('success', 'Successfully connected to backend server', 'CONNECTION');
    } catch (error) {
      setIsConnected(false);
      addLog('error', 'Failed to connect to backend server', 'CONNECTION');
    }

    // Start polling for activities
    pollIntervalRef.current = setInterval(async () => {
      try {
        const response = await window.FlightTrackerAPI.getFlights();
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
      await window.FlightTrackerAPI.clearActivityLogs();
      addLog('success', 'Backend logs cleared successfully', 'FRONTEND');
    } catch (error) {
      addLog('warning', 'Failed to clear backend logs: ' + error.message, 'FRONTEND');
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

  const getLogIcon = (level) => {
    switch (level) {
      case 'info': return 'ℹ️';
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      case 'debug': return '🔍';
      default: return '📝';
    }
  };

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString('en-GB', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return React.createElement(
    'div',
    { className: 'activities-page' },
    React.createElement(
      'div',
      { className: 'activities-header' },
      React.createElement(
        'div',
        { className: 'header-left' },
        React.createElement('h1', null, '🖥️ Activity Console'),
        React.createElement(
          'div',
          { className: 'connection-status' },
          React.createElement('span', { className: `status-dot ${isConnected ? 'connected' : 'disconnected'}` }),
          React.createElement('span', { className: 'status-text' }, isConnected ? 'Connected' : 'Disconnected')
        )
      ),
      React.createElement(
        'div',
        { className: 'header-controls' },
        React.createElement(
          'div',
          { className: 'log-stats' },
          React.createElement(
            'span',
            { className: 'stat-item' },
            React.createElement('span', { className: 'stat-label' }, 'Total:'),
            React.createElement('span', { className: 'stat-value' }, logs.length)
          ),
          React.createElement(
            'span',
            { className: 'stat-item' },
            React.createElement('span', { className: 'stat-label' }, 'Filtered:'),
            React.createElement('span', { className: 'stat-value' }, filteredLogs.length)
          )
        ),
        React.createElement('button', {
          onClick: refreshLogs,
          className: 'btn btn-primary',
          title: 'Refresh backend logs'
        }, '🔄 Refresh'),
        React.createElement('button', {
          onClick: exportLogs,
          className: 'btn btn-secondary',
          title: 'Export logs'
        }, '📄 Export'),
        React.createElement('button', {
          onClick: clearLogs,
          className: 'btn btn-danger',
          title: 'Clear all logs'
        }, '🗑️ Clear')
      )
    ),
    React.createElement(
      'div',
      { className: 'console-controls' },
      React.createElement(
        'div',
        { className: 'filter-controls' },
        React.createElement(
          'select',
          {
            value: logFilter,
            onChange: (e) => setLogFilter(e.target.value),
            className: 'log-filter-select'
          },
          React.createElement('option', { value: 'all' }, 'All Levels'),
          React.createElement('option', { value: 'info' }, 'Info'),
          React.createElement('option', { value: 'success' }, 'Success'),
          React.createElement('option', { value: 'warning' }, 'Warning'),
          React.createElement('option', { value: 'error' }, 'Error'),
          React.createElement('option', { value: 'debug' }, 'Debug')
        ),
        React.createElement('input', {
          type: 'text',
          placeholder: 'Search logs...',
          value: searchTerm,
          onChange: (e) => setSearchTerm(e.target.value),
          className: 'log-search-input'
        })
      )
    ),
    React.createElement(
      'div',
      { className: 'console-container' },
      React.createElement(
        'div',
        { className: 'console-header' },
        React.createElement('span', { className: 'console-title' }, 'Flight Tracker Console v1.0'),
        React.createElement(
          'span',
          { className: 'console-info' },
          `${filteredLogs.length} entries | Last update: ${new Date().toLocaleTimeString()}`
        )
      ),
      React.createElement(
        'div',
        { className: 'console-content' },
        filteredLogs.length === 0 ?
          React.createElement(
            'div',
            { className: 'console-empty' },
            React.createElement('p', null, 'No log entries match current filter criteria.'),
            logs.length === 0 && React.createElement('p', null, 'Starting activity monitoring...')
          ) :
          filteredLogs.map((log) =>
            React.createElement(
              'div',
              { key: log.id, className: `console-line log-${log.level}` },
              React.createElement('span', { className: 'log-timestamp' }, formatTimestamp(log.timestamp)),
              React.createElement(
                'span',
                { className: 'log-level' },
                React.createElement('span', { className: 'log-icon' }, getLogIcon(log.level)),
                log.level.toUpperCase()
              ),
              log.category && React.createElement('span', { className: 'log-category' }, `[${log.category}]`),
              React.createElement('span', { className: 'log-message' }, log.message)
            )
          )
      )
    )
  );
}

window.Activities = Activities;
