function Tracker() {
  const [flights, setFlights] = React.useState([]);
  const [currentFlight, setCurrentFlight] = React.useState(null);
  const [stats, setStats] = React.useState({
    flights_count: 0,
    elapsed_str: '00:00:00'
  });
  const [timestamp, setTimestamp] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(true);
  const [isConnected, setIsConnected] = React.useState(false);
  const [isBooting, setIsBooting] = React.useState(true);
  const [bootData, setBootData] = React.useState(null);
  const [flightRotationIndex, setFlightRotationIndex] = React.useState(0);

  // Initialize component
  React.useEffect(() => {
    initializeTracker();
    
    const interval = setInterval(() => {
      fetchData();
    }, 5000); // Poll every 5 seconds

    const rotationInterval = setInterval(() => {
      rotateCurrentFlight();
    }, 10000); // Rotate display every 10 seconds

    return () => {
      clearInterval(interval);
      clearInterval(rotationInterval);
    };
  }, []);

  const initializeTracker = async () => {
    try {
      // Reset session timer on initialization
      sessionStorage.setItem('flight-tracker-session-start', Date.now().toString());
      
      // Show boot sequence
      const bootResponse = await window.FlightTrackerAPI.getBootData();
      setBootData(bootResponse);
      setIsBooting(true);

      // Simulate boot time
      setTimeout(() => {
        setIsBooting(false);
        fetchData();
      }, 3000);

    } catch (error) {
      console.error('Failed to initialize tracker:', error);
      setIsBooting(false);
      setIsConnected(false);
      setIsLoading(false);
    }
  };

  const fetchData = async () => {
    try {
      const response = await window.FlightTrackerAPI.getFlights();
      
      setFlights(response.flights);
      
      // Calculate elapsed time from start of session (more realistic)
      const sessionStart = sessionStorage.getItem('flight-tracker-session-start');
      const startTime = sessionStart ? parseInt(sessionStart) : Date.now();
      if (!sessionStart) {
        sessionStorage.setItem('flight-tracker-session-start', startTime.toString());
      }
      
      setStats({
        flights_count: response.flights.length,
        elapsed_str: formatElapsedTime(Date.now() - startTime)
      });
      setTimestamp(new Date().toISOString());
      setIsConnected(true);
      setIsLoading(false);

      // Update current flight if flights available
      if (response.flights.length > 0 && flightRotationIndex < response.flights.length) {
        setCurrentFlight(response.flights[flightRotationIndex]);
      } else if (response.flights.length === 0) {
        setCurrentFlight(null);
        setFlightRotationIndex(0);
      }

    } catch (error) {
      console.error('Failed to fetch flight data:', error);
      setIsConnected(false);
    }
  };

  const rotateCurrentFlight = () => {
    if (flights.length > 0) {
      setFlightRotationIndex(prev => {
        const newIndex = (prev + 1) % flights.length;
        setCurrentFlight(flights[newIndex]);
        return newIndex;
      });
    }
  };

  const formatElapsedTime = (ms) => {
    const seconds = Math.floor(ms / 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return React.createElement(
    'div',
    { className: 'tracker-page' },
    React.createElement(
      'div',
      { className: 'tracker-container' },
      // Left Column - Waveshare Display Simulation
      React.createElement(
        'div',
        { className: 'tracker-display-column' },
        React.createElement(
          'div',
          { className: 'display-header' },
          React.createElement('h2', null, 'Raspberry Pi Display'),
          React.createElement(
            'div',
            { className: 'display-status' },
            React.createElement(
              'span',
              { className: `status-indicator ${isConnected ? 'connected' : 'disconnected'}` },
              isConnected ? '🟢' : '🔴'
            ),
            React.createElement(
              'span',
              { className: 'status-text' },
              isConnected ? 'Connected' : 'Disconnected'
            )
          )
        ),
        React.createElement(window.WaveshareDisplay, {
          flight: currentFlight,
          stats: stats,
          timestamp: timestamp,
          isBooting: isBooting,
          bootData: bootData
        }),
        React.createElement(
          'div',
          { className: 'display-info' },
          React.createElement(
            'p',
            { className: 'display-description' },
            'Simulates the Waveshare 2.13" e-ink display on the Raspberry Pi. Shows current tracked flight information, rotating every 10 seconds.'
          ),
          flights.length > 1 && React.createElement(
            'div',
            { className: 'rotation-indicator' },
            `Flight ${flightRotationIndex + 1} of ${flights.length}`,
            React.createElement(
              'div',
              { className: 'rotation-dots' },
              flights.map((_, index) => 
                React.createElement('span', {
                  key: index,
                  className: `dot ${index === flightRotationIndex ? 'active' : ''}`
                })
              )
            )
          )
        )
      ),
      // Right Column - Flight Board
      React.createElement(
        'div',
        { className: 'tracker-board-column' },
        React.createElement(
          'div',
          { className: 'board-header' },
          React.createElement('h2', null, 'Flight Board'),
          React.createElement(
            'div',
            { className: 'board-stats' },
            React.createElement(
              'span',
              { className: 'flight-count' },
              `${flights.length} ${flights.length === 1 ? 'Flight' : 'Flights'} Detected`
            )
          )
        ),
        React.createElement(window.FlightBoard, { currentFlights: flights }),
        React.createElement(
          'div',
          { className: 'board-info' },
          React.createElement(
            'p',
            { className: 'board-description' },
            'Rolling list of detected flights, similar to an airport departure board. Shows recent and current flights in your tracking area.'
          )
        )
      )
    ),
    // Status Bar
    React.createElement(
      'div',
      { className: 'tracker-status-bar' },
      React.createElement(
        'div',
        { className: 'status-item' },
        React.createElement('span', { className: 'label' }, 'Last Update:'),
        React.createElement('span', { className: 'value' }, timestamp || 'Never')
      ),
      React.createElement(
        'div',
        { className: 'status-item' },
        React.createElement('span', { className: 'label' }, 'Session Time:'),
        React.createElement('span', { className: 'value' }, stats.elapsed_str)
      ),
      React.createElement(
        'div',
        { className: 'status-item' },
        React.createElement('span', { className: 'label' }, 'Total Flights:'),
        React.createElement('span', { className: 'value' }, stats.flights_count)
      ),
      isLoading && React.createElement(
        'div',
        { className: 'status-item' },
        React.createElement('span', { className: 'loading-spinner' }, '⟳'),
        React.createElement('span', { className: 'value' }, 'Loading...')
      )
    )
  );
}

window.Tracker = Tracker;
