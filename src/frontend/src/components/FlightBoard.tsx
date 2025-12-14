/**
 * Flight Board component - Table view of all tracked flights
 */

import type { Flight } from '../types';
import './FlightBoard.css';

interface FlightBoardProps {
  flights: Flight[];
  currentFlights: Flight[];
}

export default function FlightBoard({ flights, currentFlights }: FlightBoardProps) {
  const currentFlightIds = new Set(currentFlights.map(f => f.registration));
  
  if (flights.length === 0) {
    return (
      <div className="flight-board-empty">
        <div className="empty-icon">✈️</div>
        <p>No flights tracked yet</p>
        <p className="empty-hint">Waiting for aircraft to enter the tracking area...</p>
      </div>
    );
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
  };

  const formatRoute = (flight: Flight) => {
    const origin = flight.origin_name || flight.origin;
    const dest = flight.destination_name || flight.destination;
    return `${origin} → ${dest}`;
  };

  return (
    <div className="flight-board">
      <div className="board-header">
        <h3>Flight History</h3>
        <div className="board-legend">
          <span className="legend-item">
            <span className="status-dot active"></span>
            Active ({currentFlights.length})
          </span>
          <span className="legend-item">
            <span className="status-dot departed"></span>
            Departed ({flights.length - currentFlights.length})
          </span>
        </div>
      </div>
      
      <div className="board-table-container">
        <table className="board-table">
          <thead>
            <tr>
              <th className="status-col">Status</th>
              <th>Time</th>
              <th>Callsign</th>
              <th>Registration</th>
              <th>Aircraft</th>
              <th>Airline</th>
              <th>Route</th>
              <th>Altitude</th>
              <th>Speed</th>
            </tr>
          </thead>
          <tbody>
            {flights.map((flight) => {
              const isActive = currentFlightIds.has(flight.registration);
              return (
                <tr key={flight.id} className={`flight-row ${isActive ? 'active' : 'departed'}`}>
                  <td className="status-col">
                    <span className={`status-indicator ${isActive ? 'active' : 'departed'}`}>
                      {isActive ? '🟢' : '⚪'}
                    </span>
                  </td>
                  <td className="time-col">{formatTime(flight.timestamp)}</td>
                  <td className="callsign">{flight.callsign}</td>
                  <td className="registration">{flight.registration}</td>
                  <td>{flight.aircraft}</td>
                  <td>{flight.airline}</td>
                  <td className="route">{formatRoute(flight)}</td>
                  <td>{flight.altitude.toLocaleString()} ft</td>
                  <td>{flight.speed} kts</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
