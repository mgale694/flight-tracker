/**
 * Waveshare 2.13" V4 E-ink Display Simulator (250x122 pixels)
 */

import type { Flight } from '../types';
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
            {/* Top row - matching view.py layout */}
            <div className="screen-row top-row">
              <span className="label">ATC: {flight.callsign}</span>
              <span className="label">COUNT: {sessionStats?.uniqueAircraft || 0}</span>
              <span className="label">TIMER: {sessionStats?.sessionDuration || '0m'}</span>
            </div>
            
            <div className="divider"></div>
            
            {/* Flight details - matching view.py */}
            <div className="screen-row detail-line">
              <span className="label">FROM: {flight.origin}</span>
            </div>
            <div className="screen-row detail-line">
              <span className="label">AIRLINE: {flight.airline}</span>
            </div>
            <div className="screen-row detail-line">
              <span className="label">MODEL: {flight.aircraft}</span>
            </div>
            <div className="screen-row detail-line">
              <span className="label">REG: {flight.registration}</span>
            </div>
            <div className="screen-row detail-line route">
              <span className="label">{flight.origin} → {flight.destination}</span>
            </div>
            
            <div className="divider"></div>
            
            {/* Bottom row - matching view.py */}
            <div className="screen-row bottom-row">
              <span className="label">ALT: {flight.altitude.toLocaleString()} ft</span>
              <span className="label">SPD: {flight.speed} kts</span>
              <span className="label">TIME: {new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
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
