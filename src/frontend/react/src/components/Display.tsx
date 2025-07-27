import React from 'react';

interface DisplayProps {
  children: React.ReactNode;
  className?: string;
}

export const Display: React.FC<DisplayProps> = ({ children, className = '' }) => {
  return (
    <div className={`raspi-display ${className}`}>
      <div className="display-screen">
        <div className="display-content">
          {children}
        </div>
      </div>
    </div>
  );
};

interface BootScreenProps {
  face: string;
  phrase: string;
  timestamp: string;
}

export const BootScreen: React.FC<BootScreenProps> = ({ face, phrase, timestamp }) => {
  const displayPhrase = phrase.length > 32 ? phrase.substring(0, 29) + '...' : phrase;

  return (
    <Display className="boot-screen">
      <div className="boot-content">
        <div className="top-line"></div>
        <div className="phrase">{displayPhrase}</div>
        <div className="face">{face}</div>
        <div className="bottom-line"></div>
        <div className="timestamp">TIME: {timestamp}</div>
      </div>
    </Display>
  );
};

interface FlightScreenProps {
  flight: {
    callsign: string;
    origin_airport_name: string;
    airline_name: string;
    aircraft_model: string;
    registration: string;
    origin_airport_iata: string;
    destination_airport_iata: string;
    altitude: string;
    ground_speed: string;
  };
  stats: {
    flights_count: number;
    elapsed_str: string;
  };
  timestamp: string;
}

export const FlightScreen: React.FC<FlightScreenProps> = ({ flight, stats, timestamp }) => {
  const fromStr = `FROM: ${flight.origin_airport_name}`;
  const displayFrom = fromStr.length > 32 ? fromStr.substring(0, 32) + '...' : fromStr;
  const route = `${flight.origin_airport_iata || 'N/A'} -> ${flight.destination_airport_iata || 'N/A'}`;

  return (
    <Display className="flight-screen">
      <div className="flight-content">
        <div className="top-row">
          <span className="callsign">ATC: {flight.callsign}</span>
          <span className="count">COUNT: {stats.flights_count}</span>
          <span className="timer">TIMER: {stats.elapsed_str}</span>
        </div>
        <div className="top-line"></div>
        <div className="flight-details">
          <div className="detail-line">{displayFrom}</div>
          <div className="detail-line">AIRLINE: {flight.airline_name}</div>
          <div className="detail-line">MODEL: {flight.aircraft_model}</div>
          <div className="detail-line">REG: {flight.registration}</div>
          <div className="detail-line">{route}</div>
        </div>
        <div className="bottom-line"></div>
        <div className="bottom-row">
          <span className="altitude">ALT: {flight.altitude} ft</span>
          <span className="speed">SPD: {flight.ground_speed} km/h</span>
          <span className="timestamp">TIME: {timestamp}</span>
        </div>
      </div>
    </Display>
  );
};
