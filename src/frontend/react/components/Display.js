function Display({ children, className = '' }) {
  return React.createElement(
    'div',
    { className: `raspi-display ${className}` },
    React.createElement(
      'div',
      { className: 'display-screen' },
      React.createElement(
        'div',
        { className: 'display-content' },
        children
      )
    )
  );
}

function BootScreen({ face, phrase, timestamp }) {
  const displayPhrase = phrase.length > 32 ? phrase.substring(0, 29) + '...' : phrase;

  return React.createElement(
    Display,
    { className: 'boot-screen' },
    React.createElement(
      'div',
      { className: 'boot-content' },
      React.createElement('div', { className: 'top-line' }),
      React.createElement('div', { className: 'phrase' }, displayPhrase),
      React.createElement('div', { className: 'face' }, face),
      React.createElement('div', { className: 'bottom-line' }),
      React.createElement('div', { className: 'timestamp' }, `TIME: ${timestamp}`)
    )
  );
}

function FlightScreen({ flight, stats, timestamp }) {
  const fromStr = `FROM: ${flight.origin_airport_name}`;
  const displayFrom = fromStr.length > 32 ? fromStr.substring(0, 32) + '...' : fromStr;
  const route = `${flight.origin_airport_iata || 'N/A'} -> ${flight.destination_airport_iata || 'N/A'}`;

  return React.createElement(
    Display,
    { className: 'flight-screen' },
    React.createElement(
      'div',
      { className: 'flight-content' },
      React.createElement(
        'div',
        { className: 'top-row' },
        React.createElement('span', { className: 'callsign' }, `ATC: ${flight.callsign}`),
        React.createElement('span', { className: 'count' }, `COUNT: ${stats.flights_count}`),
        React.createElement('span', { className: 'timer' }, `TIMER: ${stats.elapsed_str}`)
      ),
      React.createElement('div', { className: 'top-line' }),
      React.createElement(
        'div',
        { className: 'flight-details' },
        React.createElement('div', { className: 'detail-line' }, displayFrom),
        React.createElement('div', { className: 'detail-line' }, `AIRLINE: ${flight.airline_name}`),
        React.createElement('div', { className: 'detail-line' }, `MODEL: ${flight.aircraft_model}`),
        React.createElement('div', { className: 'detail-line' }, `REG: ${flight.registration}`),
        React.createElement('div', { className: 'detail-line' }, route)
      ),
      React.createElement('div', { className: 'bottom-line' }),
      React.createElement(
        'div',
        { className: 'bottom-row' },
        React.createElement('span', { className: 'altitude' }, `ALT: ${flight.altitude} ft`),
        React.createElement('span', { className: 'speed' }, `SPD: ${flight.ground_speed} km/h`),
        React.createElement('span', { className: 'timestamp' }, `TIME: ${timestamp}`)
      )
    )
  );
}

window.Display = Display;
window.BootScreen = BootScreen;
window.FlightScreen = FlightScreen;
