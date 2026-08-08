import { useMemo } from 'react';
import type { LocationPreview } from '../types';
import './ViewingZoneEditor.css';

interface ViewingZoneEditorProps {
  bearing: number;
  fieldOfView: number;
  maxDistance: number;
  location?: LocationPreview | null;
  onBearingChange: (value: number) => void;
  onFieldOfViewChange: (value: number) => void;
  onMaxDistanceChange: (value: number) => void;
}

const CARDINAL_DIRECTIONS = [
  { label: 'N', bearing: 0 },
  { label: 'NE', bearing: 45 },
  { label: 'E', bearing: 90 },
  { label: 'SE', bearing: 135 },
  { label: 'S', bearing: 180 },
  { label: 'SW', bearing: 225 },
  { label: 'W', bearing: 270 },
  { label: 'NW', bearing: 315 },
];

function polarPoint(
  bearing: number,
  radius: number,
  centreX = 120,
  centreY = 132,
): { x: number; y: number } {
  const radians = (bearing * Math.PI) / 180;
  return {
    x: centreX + Math.sin(radians) * radius,
    y: centreY - Math.cos(radians) * radius,
  };
}

function viewingSectorPath(
  bearing: number,
  fieldOfView: number,
  radius = 104,
  centreX = 120,
  centreY = 132,
): string {
  const start = polarPoint(bearing - fieldOfView / 2, radius, centreX, centreY);
  const end = polarPoint(bearing + fieldOfView / 2, radius, centreX, centreY);
  const largeArc = fieldOfView > 180 ? 1 : 0;
  return `M ${centreX} ${centreY} L ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y} Z`;
}

export default function ViewingZoneEditor({
  bearing,
  fieldOfView,
  maxDistance,
  location,
  onBearingChange,
  onFieldOfViewChange,
  onMaxDistanceChange,
}: ViewingZoneEditorProps) {
  const sectorPath = useMemo(
    () => viewingSectorPath(bearing, fieldOfView),
    [bearing, fieldOfView],
  );
  const mapDetails = useMemo(() => {
    if (!location) return null;
    const latitudeSpan = 55 / 111;
    const longitudeSpan = 55 / (
      111 * Math.max(Math.cos((location.latitude * Math.PI) / 180), 0.2)
    );
    const bounds = [
      location.longitude - longitudeSpan,
      location.latitude - latitudeSpan,
      location.longitude + longitudeSpan,
      location.latitude + latitudeSpan,
    ].join(',');
    const query = new URLSearchParams({
      bbox: bounds,
      layer: 'mapnik',
      marker: `${location.latitude},${location.longitude}`,
    });
    const radius = Math.max(8, Math.min(94, (maxDistance / 50) * 94));
    return {
      embedUrl: `https://www.openstreetmap.org/export/embed.html?${query.toString()}`,
      mapUrl: `https://www.openstreetmap.org/?mlat=${location.latitude}&mlon=${location.longitude}#map=11/${location.latitude}/${location.longitude}`,
      sectorPath: viewingSectorPath(bearing, fieldOfView, radius, 120, 100),
    };
  }, [bearing, fieldOfView, location, maxDistance]);

  return (
    <div className="viewing-preview-grid">
      <div className="viewing-controls">
        <fieldset>
          <legend>Which way does the window face?</legend>
          <div className="cardinal-grid">
            {CARDINAL_DIRECTIONS.map((direction) => (
              <button
                type="button"
                key={direction.label}
                className={bearing === direction.bearing ? 'selected' : ''}
                onClick={() => onBearingChange(direction.bearing)}
                aria-pressed={bearing === direction.bearing}
              >
                {direction.label}
              </button>
            ))}
          </div>
        </fieldset>

        <label htmlFor="bearing">Fine direction: {bearing}°</label>
        <input
          id="bearing"
          type="range"
          min="0"
          max="359"
          value={bearing}
          onChange={(event) => onBearingChange(Number(event.target.value))}
        />

        <label htmlFor="field-of-view">Visible width: {fieldOfView}°</label>
        <input
          id="field-of-view"
          type="range"
          min="20"
          max="180"
          step="5"
          value={fieldOfView}
          onChange={(event) => onFieldOfViewChange(Number(event.target.value))}
        />

        <label htmlFor="view-distance">Clear viewing distance: {maxDistance} km</label>
        <input
          id="view-distance"
          type="range"
          min="1"
          max="50"
          value={maxDistance}
          onChange={(event) => onMaxDistanceChange(Number(event.target.value))}
        />
      </div>

      {mapDetails && location ? (
        <div className="viewing-map">
          <div className="map-canvas">
            <iframe
              src={mapDetails.embedUrl}
              title={`Map centred on ${location.formatted_address}`}
              loading="lazy"
              tabIndex={-1}
              referrerPolicy="strict-origin-when-cross-origin"
            />
            <svg
              viewBox="0 0 240 200"
              preserveAspectRatio="none"
              role="img"
              className="map-sector-overlay"
            >
              <title>Grey flight search area from the selected address</title>
              <path d={mapDetails.sectorPath} className="map-search-sector" />
              <circle cx="120" cy="100" r="5" className="map-observer" />
            </svg>
          </div>
          <div className="resolved-location">
            <span>Resolved window location</span>
            <strong>{location.formatted_address}</strong>
            <a href={mapDetails.mapUrl} target="_blank" rel="noreferrer">
              View larger map
            </a>
            <a
              href="https://www.openstreetmap.org/copyright"
              target="_blank"
              rel="noreferrer"
            >
              Map data: OpenStreetMap contributors
            </a>
          </div>
          <div className="map-summary">
            <strong>{bearing}° · {fieldOfView}° view</strong>
            <span>Grey area · up to {maxDistance} km</span>
          </div>
        </div>
      ) : (
        <div className="viewing-diagram" aria-label="Top-down preview of the viewing zone">
          <svg viewBox="0 0 240 160" role="img">
            <title>Window viewing direction and field of view</title>
            <path d={sectorPath} className="viewing-sector" />
            <circle cx="120" cy="132" r="9" className="observer" />
            <line x1="120" y1="8" x2="120" y2="20" className="north-marker" />
            <text x="120" y="7" textAnchor="middle">N</text>
          </svg>
          <strong>{bearing}° · {fieldOfView}° view</strong>
          <span>Resolve an address to preview the search area on a map</span>
        </div>
      )}
    </div>
  );
}
