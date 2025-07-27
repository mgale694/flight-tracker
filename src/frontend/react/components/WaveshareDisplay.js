function WaveshareDisplay({ 
  flight, 
  stats, 
  timestamp, 
  isBooting = false, 
  bootData 
}) {
  // Format timestamp to show only time (HH:MM:SS)
  const formatTimeOnly = (timestampStr) => {
    try {
      const date = new Date(timestampStr);
      // Check if the date is valid
      if (isNaN(date.getTime())) {
        // If invalid, try to parse it as just time
        if (timestampStr.includes(':')) {
          return timestampStr.split(' ').pop() || timestampStr;
        }
        // Fallback to current time
        return new Date().toLocaleTimeString('en-GB', { 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit',
          hour12: false 
        });
      }
      return date.toLocaleTimeString('en-GB', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        hour12: false 
      });
    } catch {
      // Fallback: return current time
      return new Date().toLocaleTimeString('en-GB', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        hour12: false 
      });
    }
  };

  if (isBooting && bootData) {
    return React.createElement(
      'div',
      { className: 'waveshare-display' },
      React.createElement(
        'div',
        { className: 'waveshare-screen boot-mode' },
        React.createElement(
          'div',
          { className: 'display-content' },
          React.createElement('div', { className: 'boot-header' }),
          React.createElement(
            'div',
            { className: 'boot-body' },
            React.createElement('div', { className: 'boot-phrase' }, bootData.phrase),
            React.createElement('div', { className: 'boot-face' }, bootData.face),
            React.createElement('div', { className: 'boot-message' }, bootData.message)
          ),
          React.createElement(
            'div',
            { className: 'boot-footer' },
            React.createElement('div', { className: 'timestamp-line' }, `TIME: ${formatTimeOnly(timestamp)}`)
          )
        )
      )
    );
  }

  if (!flight) {
    return React.createElement(
      'div',
      { className: 'waveshare-display' },
      React.createElement(
        'div',
        { className: 'waveshare-screen scanning-mode' },
        React.createElement(
          'div',
          { className: 'display-content' },
          React.createElement(
            'div',
            { className: 'scan-header' },
            React.createElement('span', { className: 'count-info' }, `COUNT: ${stats.flights_count}`),
            React.createElement('span', { className: 'timer-info' }, `TIMER: ${stats.elapsed_str}`)
          ),
          React.createElement(
            'div',
            { className: 'scan-body' },
            React.createElement('div', { className: 'scan-status' }, 'SCANNING...'),
            React.createElement('div', { className: 'scan-subtitle' }, 'Waiting for aircraft'),
            React.createElement(
              'div',
              { className: 'scan-animation' },
              React.createElement('span', { className: 'scan-dot' }, '●'),
              React.createElement('span', { className: 'scan-dot' }, '●'),
              React.createElement('span', { className: 'scan-dot' }, '●')
            )
          ),
          React.createElement(
            'div',
            { className: 'scan-footer' },
            React.createElement('span', { className: 'timestamp-info' }),
            React.createElement('span', { className: 'timestamp-info' }),
            React.createElement('span', { className: 'timestamp-info' }, `TIME: ${formatTimeOnly(timestamp)}`)
          )
        )
      )
    );
  }

  // Flight display mode
  const fromStr = `FROM: ${flight.origin_airport_name || 'Unknown'}`;
  const displayFrom = fromStr.length > 30 ? fromStr.substring(0, 27) + '...' : fromStr;
  const route = `${flight.origin_airport_iata || 'N/A'} → ${flight.destination_airport_iata || 'N/A'}`;
  
  return React.createElement(
    'div',
    { className: 'waveshare-display' },
    React.createElement(
      'div',
      { className: 'waveshare-screen flight-mode' },
      React.createElement(
        'div',
        { className: 'display-content' },
        React.createElement(
          'div',
          { className: 'flight-header' },
          React.createElement('span', { className: 'callsign-info' }, `ATC: ${flight.callsign || 'N/A'}`),
          React.createElement('span', { className: 'count-info' }, `COUNT: ${stats.flights_count}`),
          React.createElement('span', { className: 'timer-info' }, `TIMER: ${stats.elapsed_str}`)
        ),
        React.createElement(
          'div',
          { className: 'flight-details' },
          React.createElement('div', { className: 'detail-row' }, displayFrom),
          React.createElement('div', { className: 'detail-row' }, `AIRLINE: ${flight.airline_name || 'Unknown'}`),
          React.createElement('div', { className: 'detail-row' }, `MODEL: ${flight.aircraft_model || 'N/A'}`),
          React.createElement('div', { className: 'detail-row' }, `REG: ${flight.registration || 'N/A'}`),
          React.createElement('div', { className: 'detail-row route-row' }, route)
        ),
        React.createElement(
          'div',
          { className: 'flight-footer' },
          React.createElement('span', { className: 'alt-info' }, `ALT: ${flight.altitude || 'N/A'} ft`),
          React.createElement('span', { className: 'speed-info' }, `SPD: ${flight.ground_speed || 'N/A'} kt`),
          React.createElement('span', { className: 'timestamp-info' }, `TIME: ${formatTimeOnly(timestamp)}`)
        )
      )
    )
  );
}

window.WaveshareDisplay = WaveshareDisplay;
