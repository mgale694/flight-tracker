import type { Flight } from '../types';
import './WaveshareDisplay.css';

interface WaveshareDisplayProps {
  flight: Flight | null;
  showBootScreen?: boolean;
  showScanScreen?: boolean;
}

export default function WaveshareDisplay({
  flight,
  showBootScreen = false,
  showScanScreen = false,
}: WaveshareDisplayProps) {
  const route = flight ? `${flight.origin || '—'} → ${flight.destination || '—'}` : '';
  const aircraft = flight?.aircraft && flight.aircraft !== 'Unknown' ? flight.aircraft : null;
  const distance = flight ? `${(flight.distance / 1000).toFixed(1)} km` : null;

  return (
    <figure className="waveshare-display">
      <div className="display-shell">
        <div className="display-screen">
          {showBootScreen && (
            <div className="eink-centred-state">
              <span className="eink-kicker">FLIGHT TRACKER</span>
              <strong>Starting quietly.</strong>
              <span>Opening your view of the sky…</span>
            </div>
          )}

          {showScanScreen && !showBootScreen && (
            <div className="eink-centred-state">
              <span className="eink-kicker">WINDOW VIEW</span>
              <strong>Watching the sky.</strong>
              <span>No aircraft are visible just now.</span>
            </div>
          )}

          {!showBootScreen && !showScanScreen && flight && (
            <div className="eink-flight">
              <div className="eink-topline">
                <span>AIRCRAFT IN VIEW</span>
                <span>{Math.round(flight.heading)}°</span>
              </div>
              <strong className="eink-flight-number">
                {flight.callsign || flight.registration || 'AIRCRAFT'}
              </strong>
              <div className="eink-route">{route}</div>
              <div className="eink-aircraft">
                <span>{aircraft || 'Aircraft type unavailable'}</span>
                {flight.registration && <span>{flight.registration}</span>}
              </div>
              <div className="eink-bottomline">
                <span>{flight.altitude.toLocaleString()} ft</span>
                <span>{distance}</span>
              </div>
            </div>
          )}

          {!showBootScreen && !showScanScreen && !flight && (
            <div className="eink-centred-state">
              <strong>Waiting for a view.</strong>
              <span>Complete display setup to begin.</span>
            </div>
          )}
        </div>
      </div>
      <figcaption>2.13-inch e-paper · semantic preview</figcaption>
    </figure>
  );
}
