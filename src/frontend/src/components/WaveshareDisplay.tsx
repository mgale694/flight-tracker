/**
 * Waveshare 2.13" V4 E-ink Display Simulator (250x122 pixels)
 */

import { Flight } from '../types';
import './WaveshareDisplay.css';

interface WaveshareDisplayProps {
  flight: Flight | null;
  sessionStats?: {
    flightsDetected: number;
    uniqueAircraft: number;
    sessionDuration: string;
  };
  showBootScreen?: boolean;
  showScanScreen?: boolean;
}

export default function WaveshareDisplay({ 
  flight, 
  sessionStats,
  showBootScreen = false,
  showScanScreen = false
}: WaveshareDisplayProps) {
  return (
    <div className="waveshare-display">
      <div className="display-screen">
        {showBootScreen && (
          <div className="boot-screen">
            <pre className="ascii-art">
{`  ✈️ FLIGHT  
  TRACKER`}
            </pre>
            <p className="boot-text">Initializing...</p>
          </div>
        )}
        
        {showScanScreen && !showBootScreen && (
          <div className="scan-screen">
            <p className="scan-text">🔍 Scanning...</p>
            <p className="scan-subtext">Looking for aircraft</p>
          </div>
        )}
        
        {!showBootScreen && !showScanScreen && flight && (
          <div className="flight-screen">
            <div className="flight-header">
              <span className="callsign">{flight.callsign}</span>
              <span className="aircraft">{flight.aircraft}</span>
            </div>
            
            <div className="flight-route">
              <span>{flight.origin}</span>
              <span> → </span>
              <span>{flight.destination}</span>
            </div>
            
            <div className="flight-details">
              <div className="detail-row">
                <span>ALT:</span>
                <span>{flight.altitude.toLocaleString()} ft</span>
              </div>
              <div className="detail-row">
                <span>SPD:</span>
                <span>{flight.speed} kts</span>
              </div>
              <div className="detail-row">
                <span>DST:</span>
                <span>{(flight.distance / 1000).toFixed(1)} km</span>
              </div>
            </div>
            
            <div className="flight-footer">
              <span className="registration">{flight.registration}</span>
              <span className="airline">{flight.airline}</span>
            </div>
          </div>
        )}
        
        {!showBootScreen && !showScanScreen && !flight && (
          <div className="no-flights">
            <p>No flights detected</p>
            {sessionStats && (
              <div className="stats">
                <p className="stat-line">Detected: {sessionStats.flightsDetected}</p>
                <p className="stat-line">Unique: {sessionStats.uniqueAircraft}</p>
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="display-label">Waveshare 2.13" V4 (250x122)</div>
    </div>
  );
}
