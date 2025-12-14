/**
 * Flight Board component - Table view of all flights
 */

import { Flight } from '../types';
import './FlightBoard.css';

interface FlightBoardProps {
  flights: Flight[];
}

export default function FlightBoard({ flights }: FlightBoardProps) {
  if (flights.length === 0) {
    return (
      <div className="flight-board-empty">
        <p>No flights detected in the area</p>
      </div>
    );
  }

  return (
    <div className="flight-board">
      <div className="board-header">
        <h3>Detected Flights ({flights.length})</h3>
      </div>
      
      <div className="board-table-container">
        <table className="board-table">
          <thead>
            <tr>
              <th>Callsign</th>
              <th>Aircraft</th>
              <th>Airline</th>
              <th>Route</th>
              <th>Altitude</th>
              <th>Speed</th>
              <th>Distance</th>
            </tr>
          </thead>
          <tbody>
            {flights.map((flight) => (
              <tr key={flight.id} className="flight-row">
                <td className="callsign">{flight.callsign}</td>
                <td>{flight.aircraft}</td>
                <td>{flight.airline}</td>
                <td className="route">
                  {flight.origin} → {flight.destination}
                </td>
                <td>{flight.altitude.toLocaleString()} ft</td>
                <td>{flight.speed} kts</td>
                <td>{(flight.distance / 1000).toFixed(1)} km</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
