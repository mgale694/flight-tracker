import React, { useState, useEffect } from 'react';
import type { FlightData } from '../types';

interface FlightBoardEntry extends FlightData {
  firstSeen: Date;
  lastSeen: Date;
  status: 'overhead' | 'departed' | 'tracking';
}

interface FlightBoardProps {
  currentFlights: FlightData[];
}

export const FlightBoard: React.FC<FlightBoardProps> = ({ currentFlights }) => {
  const [boardFlights, setBoardFlights] = useState<FlightBoardEntry[]>([]);

  useEffect(() => {
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'overhead': return '✈️';
      case 'departed': return '🛫';
      case 'tracking': return '📡';
      default: return '❓';
    }
  };

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'overhead': return 'status-overhead';
      case 'departed': return 'status-departed';
      case 'tracking': return 'status-tracking';
      default: return 'status-unknown';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-GB', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      hour12: false 
    });
  };

  const formatDuration = (start: Date, end: Date) => {
    const diffMs = end.getTime() - start.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const mins = Math.floor(diffSecs / 60);
    const secs = diffSecs % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flight-board">
      <div className="flight-board-header">
        <h2>Flight Departures</h2>
        <div className="board-stats">
          <span className="stat">
            <span className="stat-icon">✈️</span>
            <span className="stat-count">{boardFlights.filter(f => f.status === 'overhead').length}</span>
            <span className="stat-label">Overhead</span>
          </span>
          <span className="stat">
            <span className="stat-icon">🛫</span>
            <span className="stat-count">{boardFlights.filter(f => f.status === 'departed').length}</span>
            <span className="stat-label">Departed</span>
          </span>
          <span className="stat">
            <span className="stat-icon">📊</span>
            <span className="stat-count">{boardFlights.length}</span>
            <span className="stat-label">Total</span>
          </span>
        </div>
      </div>

      <div className="flight-board-content">
        <div className="board-table-header">
          <div className="col-time">Time</div>
          <div className="col-callsign">Flight</div>
          <div className="col-route">Route</div>
          <div className="col-altitude">Altitude</div>
          <div className="col-speed">Speed</div>
          <div className="col-duration">Duration</div>
          <div className="col-status">Status</div>
        </div>

        <div className="board-table-body">
          {boardFlights.length === 0 ? (
            <div className="board-empty">
              <div className="empty-icon">🔍</div>
              <div className="empty-text">No flights tracked yet</div>
              <div className="empty-subtext">Flights will appear here when detected</div>
            </div>
          ) : (
            boardFlights.map((flight) => (
              <div 
                key={`${flight.id}-${flight.firstSeen.getTime()}`} 
                className={`board-row ${getStatusClass(flight.status)}`}
              >
                <div className="col-time">
                  {formatTime(flight.firstSeen)}
                </div>
                <div className="col-callsign">
                  <span className="callsign-text">{flight.callsign || 'N/A'}</span>
                  <span className="registration-text">{flight.registration || ''}</span>
                </div>
                <div className="col-route">
                  <span className="route-text">
                    {flight.origin_airport_iata || 'N/A'} → {flight.destination_airport_iata || 'N/A'}
                  </span>
                  <span className="airline-text">{flight.airline_name || ''}</span>
                </div>
                <div className="col-altitude">
                  {flight.altitude || 'N/A'} ft
                </div>
                <div className="col-speed">
                  {flight.ground_speed || 'N/A'} kt
                </div>
                <div className="col-duration">
                  {formatDuration(flight.firstSeen, flight.lastSeen)}
                </div>
                <div className="col-status">
                  <span className="status-icon">{getStatusIcon(flight.status)}</span>
                  <span className="status-text">{flight.status}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
