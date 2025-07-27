function FlightBoard({ currentFlights }) {
  const [boardFlights, setBoardFlights] = React.useState([]);

  React.useEffect(() => {
    const now = new Date();
    
    // Update the board with current flights
    setBoardFlights(prev => {
      const newBoard = [...prev];
      
      // Add new flights
      currentFlights.forEach(flight => {
        const existingIndex = newBoard.findIndex(bf => bf.id === flight.id);
        
        if (existingIndex >= 0) {
          // Update existing flight
          newBoard[existingIndex] = {
            ...newBoard[existingIndex],
            ...flight,
            lastSeen: now,
            status: 'overhead'
          };
        } else {
          // Add new flight
          newBoard.unshift({
            ...flight,
            firstSeen: now,
            lastSeen: now,
            status: 'overhead'
          });
        }
      });
      
      // Update status of flights not currently overhead
      newBoard.forEach((boardFlight, index) => {
        const stillOverhead = currentFlights.some(cf => cf.id === boardFlight.id);
        const timeSinceLastSeen = now.getTime() - boardFlight.lastSeen.getTime();
        
        if (!stillOverhead) {
          if (timeSinceLastSeen < 30000) { // 30 seconds
            newBoard[index].status = 'departed';
          } else {
            newBoard[index].status = 'tracking';
          }
        }
      });
      
      // Remove old flights (keep last 50)
      return newBoard
        .sort((a, b) => b.lastSeen.getTime() - a.lastSeen.getTime())
        .slice(0, 50);
    });
  }, [currentFlights]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'overhead': return '✈️';
      case 'departed': return '🛫';
      case 'tracking': return '📡';
      default: return '❓';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'overhead': return 'status-overhead';
      case 'departed': return 'status-departed';
      case 'tracking': return 'status-tracking';
      default: return 'status-unknown';
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-GB', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      hour12: false 
    });
  };

  const formatDuration = (start, end) => {
    const diffMs = end.getTime() - start.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const mins = Math.floor(diffSecs / 60);
    const secs = diffSecs % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return React.createElement(
    'div',
    { className: 'flight-board' },
    React.createElement(
      'div',
      { className: 'flight-board-header' },
      React.createElement('h2', null, 'Flight Departures'),
      React.createElement(
        'div',
        { className: 'board-stats' },
        React.createElement(
          'span',
          { className: 'stat' },
          React.createElement('span', { className: 'stat-icon' }, '✈️'),
          React.createElement('span', { className: 'stat-count' }, boardFlights.filter(f => f.status === 'overhead').length),
          React.createElement('span', { className: 'stat-label' }, 'Overhead')
        ),
        React.createElement(
          'span',
          { className: 'stat' },
          React.createElement('span', { className: 'stat-icon' }, '🛫'),
          React.createElement('span', { className: 'stat-count' }, boardFlights.filter(f => f.status === 'departed').length),
          React.createElement('span', { className: 'stat-label' }, 'Departed')
        ),
        React.createElement(
          'span',
          { className: 'stat' },
          React.createElement('span', { className: 'stat-icon' }, '📊'),
          React.createElement('span', { className: 'stat-count' }, boardFlights.length),
          React.createElement('span', { className: 'stat-label' }, 'Total')
        )
      )
    ),
    React.createElement(
      'div',
      { className: 'flight-board-content' },
      React.createElement(
        'div',
        { className: 'board-table-header' },
        React.createElement('div', { className: 'col-time' }, 'Time'),
        React.createElement('div', { className: 'col-callsign' }, 'Flight'),
        React.createElement('div', { className: 'col-route' }, 'Route'),
        React.createElement('div', { className: 'col-altitude' }, 'Altitude'),
        React.createElement('div', { className: 'col-speed' }, 'Speed'),
        React.createElement('div', { className: 'col-duration' }, 'Duration'),
        React.createElement('div', { className: 'col-status' }, 'Status')
      ),
      React.createElement(
        'div',
        { className: 'board-table-body' },
        boardFlights.length === 0 ? 
          React.createElement(
            'div',
            { className: 'board-empty' },
            React.createElement('div', { className: 'empty-icon' }, '🔍'),
            React.createElement('div', { className: 'empty-text' }, 'No flights tracked yet'),
            React.createElement('div', { className: 'empty-subtext' }, 'Flights will appear here when detected')
          ) :
          boardFlights.map((flight) => 
            React.createElement(
              'div',
              { 
                key: `${flight.id}-${flight.firstSeen.getTime()}`,
                className: `board-row ${getStatusClass(flight.status)}`
              },
              React.createElement(
                'div',
                { className: 'col-time' },
                formatTime(flight.firstSeen)
              ),
              React.createElement(
                'div',
                { className: 'col-callsign' },
                React.createElement('span', { className: 'callsign-text' }, flight.callsign || 'N/A'),
                React.createElement('span', { className: 'registration-text' }, flight.registration || '')
              ),
              React.createElement(
                'div',
                { className: 'col-route' },
                React.createElement('span', { className: 'route-text' }, 
                  `${flight.origin_airport_iata || 'N/A'} → ${flight.destination_airport_iata || 'N/A'}`
                ),
                React.createElement('span', { className: 'airline-text' }, flight.airline_name || '')
              ),
              React.createElement('div', { className: 'col-altitude' }, `${flight.altitude || 'N/A'} ft`),
              React.createElement('div', { className: 'col-speed' }, `${flight.ground_speed || 'N/A'} kt`),
              React.createElement('div', { className: 'col-duration' }, formatDuration(flight.firstSeen, flight.lastSeen)),
              React.createElement(
                'div',
                { className: 'col-status' },
                React.createElement('span', { className: 'status-icon' }, getStatusIcon(flight.status)),
                React.createElement('span', { className: 'status-text' }, flight.status)
              )
            )
          )
      )
    )
  );
}

window.FlightBoard = FlightBoard;
