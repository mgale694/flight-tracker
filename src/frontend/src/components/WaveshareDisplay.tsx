/**
 * Waveshare 2.13" V4 E-ink Display Simulator (250x122 pixels)
 */

import { useEffect, useState } from 'react';
import type { Flight } from '../types';
import { api } from '../api';
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
  const [displayFields, setDisplayFields] = useState<string[]>(['FROM', 'AIRLINE', 'MODEL', 'REG', 'ROUTE']);

  useEffect(() => {
    // Load display fields from config
    api.getConfig().then(config => {
      if (config.main.display_fields) {
        setDisplayFields(config.main.display_fields);
      }
    }).catch(err => {
      console.error('Failed to load config:', err);
    });
  }, []);

  const getFieldValue = (fieldId: string): string => {
    if (!flight) return 'N/A';

    const origin_name = flight.origin_name;
    const origin_code = flight.origin || 'N/A';
    const dest_name = flight.destination_name;
    const dest_code = flight.destination || 'N/A';

    // Display full name with code, or just code if name not available
    const origin_display = origin_name && origin_name !== origin_code 
      ? `${origin_name} (${origin_code})` 
      : origin_code;
    
    const dest_display = dest_name && dest_name !== dest_code 
      ? `${dest_name} (${dest_code})` 
      : dest_code;

    const fieldMap: Record<string, string> = {
      'FROM': `FROM: ${origin_display}`,
      'TO': `TO: ${dest_display}`,
      'AIRLINE': `AIRLINE: ${flight.airline || 'N/A'}`,
      'MODEL': `MODEL: ${flight.aircraft || 'Unknown'}`,
      'REG': `REG: ${flight.registration || 'N/A'}`,
      'ROUTE': `${origin_code} → ${dest_code}`,
      'callsign': `CALLSIGN: ${flight.callsign || 'N/A'}`,
      'registration': `REG: ${flight.registration || 'N/A'}`,
      'altitude': `ALT: ${flight.altitude} ft`,
      'speed': `SPD: ${flight.speed} kts`,
      'heading': `HDG: ${flight.heading}°`,
      'distance': `DIST: ${Math.round(flight.distance)} m`,
    };

    return fieldMap[fieldId] || fieldId;
  };

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
            
            {/* Dynamic fields based on configuration */}
            {displayFields.slice(0, 5).map((fieldId, index) => (
              <div key={index} className="screen-row detail-line">
                <span className="label">{getFieldValue(fieldId)}</span>
              </div>
            ))}
            
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
