import React from 'react';
import type { FlightData } from '../types';

interface WaveshareDisplayProps {
  flight: FlightData | null;
  stats: {
    flights_count: number;
    elapsed_str: string;
  };
  timestamp: string;
  isBooting?: boolean;
  bootData?: {
    face: string;
    phrase: string;
    message: string;
  };
}

export const WaveshareDisplay: React.FC<WaveshareDisplayProps> = ({ 
  flight, 
  stats, 
  timestamp, 
  isBooting = false, 
  bootData 
}) => {
  if (isBooting && bootData) {
    return (
      <div className="waveshare-display">
        <div className="waveshare-screen boot-mode">
          <div className="display-content">
            <div className="boot-header">
              <div className="divider-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
            </div>
            
            <div className="boot-body">
              <div className="boot-phrase">{bootData.phrase}</div>
              <div className="boot-face">{bootData.face}</div>
              <div className="boot-message">{bootData.message}</div>
            </div>
            
            <div className="boot-footer">
              <div className="divider-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
              <div className="timestamp-line">TIME: {timestamp}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!flight) {
    return (
      <div className="waveshare-display">
        <div className="waveshare-screen scanning-mode">
          <div className="display-content">
            <div className="scan-header">
              <span className="count-info">COUNT: {stats.flights_count}</span>
              <span className="timer-info">TIMER: {stats.elapsed_str}</span>
            </div>
            
            <div className="divider-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
            
            <div className="scan-body">
              <div className="scan-status">SCANNING...</div>
              <div className="scan-subtitle">Waiting for aircraft</div>
              <div className="scan-animation">
                <span className="scan-dot">●</span>
                <span className="scan-dot">●</span>
                <span className="scan-dot">●</span>
              </div>
            </div>
            
            <div className="divider-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
            
            <div className="scan-footer">
              <span className="status-info">READY</span>
              <span className="timestamp-info">TIME: {timestamp}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Flight display mode
  const fromStr = `FROM: ${flight.origin_airport_name || 'Unknown'}`;
  const displayFrom = fromStr.length > 30 ? fromStr.substring(0, 27) + '...' : fromStr;
  const route = `${flight.origin_airport_iata || 'N/A'} → ${flight.destination_airport_iata || 'N/A'}`;
  
  return (
    <div className="waveshare-display">
      <div className="waveshare-screen flight-mode">
        <div className="display-content">
          <div className="flight-header">
            <span className="callsign-info">ATC: {flight.callsign || 'N/A'}</span>
            <span className="count-info">COUNT: {stats.flights_count}</span>
            <span className="timer-info">TIMER: {stats.elapsed_str}</span>
          </div>
          
          <div className="divider-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
          
          <div className="flight-details">
            <div className="detail-row">{displayFrom}</div>
            <div className="detail-row">AIRLINE: {flight.airline_name || 'Unknown'}</div>
            <div className="detail-row">MODEL: {flight.aircraft_model || 'N/A'}</div>
            <div className="detail-row">REG: {flight.registration || 'N/A'}</div>
            <div className="detail-row route-row">{route}</div>
          </div>
          
          <div className="divider-line">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>
          
          <div className="flight-footer">
            <span className="alt-info">ALT: {flight.altitude || 'N/A'} ft</span>
            <span className="speed-info">SPD: {flight.ground_speed || 'N/A'} kt</span>
            <span className="timestamp-info">TIME: {timestamp}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
