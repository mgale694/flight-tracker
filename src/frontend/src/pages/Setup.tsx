import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import './Setup.css';

type SetupStep = 'account' | 'window' | 'complete';

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

function polarPoint(bearing: number, radius: number): { x: number; y: number } {
  const radians = (bearing * Math.PI) / 180;
  return {
    x: 120 + Math.sin(radians) * radius,
    y: 132 - Math.cos(radians) * radius,
  };
}

function viewingSectorPath(bearing: number, fieldOfView: number): string {
  const radius = 104;
  const start = polarPoint(bearing - fieldOfView / 2, radius);
  const end = polarPoint(bearing + fieldOfView / 2, radius);
  const largeArc = fieldOfView > 180 ? 1 : 0;
  return `M 120 132 L ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y} Z`;
}

export default function Setup() {
  const [searchParams] = useSearchParams();
  const storedEmail = localStorage.getItem('flight-tracker-development-email') || '';
  const [step, setStep] = useState<SetupStep>(storedEmail ? 'window' : 'account');
  const [email, setEmail] = useState(storedEmail);
  const [deviceId, setDeviceId] = useState(
    searchParams.get('d') || searchParams.get('device') || 'dev-kit-001',
  );
  const [pairingCode, setPairingCode] = useState(
    searchParams.get('c') || searchParams.get('code') || '',
  );
  const [address, setAddress] = useState('');
  const [bearing, setBearing] = useState(0);
  const [fieldOfView, setFieldOfView] = useState(80);
  const [maxDistance, setMaxDistance] = useState(35);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sectorPath = useMemo(
    () => viewingSectorPath(bearing, fieldOfView),
    [bearing, fieldOfView],
  );

  useEffect(() => {
    let active = true;
    api.getPairingStatus(deviceId)
      .then((status) => {
        if (active && status.paired) setStep('complete');
      })
      .catch(() => {
        // Manual entry remains available when the code/device has not been confirmed yet.
      });
    return () => {
      active = false;
    };
  }, [deviceId]);

  const continueWithDevelopmentAccount = (event: FormEvent) => {
    event.preventDefault();
    localStorage.setItem('flight-tracker-development-email', email.trim());
    setStep('window');
  };

  const completeSetup = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.updateConfig({
        address: address.trim(),
        search_radius_meters: Math.round(maxDistance * 1000),
        bearing_degrees: bearing,
        field_of_view_degrees: fieldOfView,
        min_distance_km: 0,
        max_distance_km: maxDistance,
      });
      await api.pairDevice(deviceId.trim(), pairingCode.trim());
      setStep('complete');
    } catch (setupError) {
      setError(setupError instanceof Error ? setupError.message : 'Setup could not be completed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="setup-page">
      <section className="setup-intro">
        <span className="eyebrow">Display setup</span>
        <h1>Point your window at the sky.</h1>
        <p>
          Pair the e-paper display, tell us where the window faces, and we’ll
          identify aircraft inside that view.
        </p>
        <ol className="setup-progress" aria-label="Setup progress">
          <li className={step === 'account' ? 'current' : 'done'}>Account</li>
          <li className={step === 'window' ? 'current' : step === 'complete' ? 'done' : ''}>
            Window
          </li>
          <li className={step === 'complete' ? 'current' : ''}>Ready</li>
        </ol>
      </section>

      <section className="setup-card">
        {step === 'account' && (
          <form onSubmit={continueWithDevelopmentAccount}>
            <span className="step-number">01</span>
            <h2>Sign in to continue</h2>
            <p className="setup-copy">
              Your displays and window settings will belong to this account.
            </p>
            <label htmlFor="setup-email">Email address</label>
            <input
              id="setup-email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
            />
            <button type="submit" className="primary-action">Continue with email</button>
            <p className="development-note">
              Development sign-in is active for the prototype. Secure account sessions
              replace this local-only identity in the persistence/auth phase.
            </p>
          </form>
        )}

        {step === 'window' && (
          <form onSubmit={completeSetup}>
            <span className="step-number">02</span>
            <h2>Describe what you can see</h2>
            <p className="setup-copy">
              Start broad. You can fine-tune the viewing zone later.
            </p>

            {error && <div className="setup-error" role="alert">{error}</div>}

            <div className="pairing-fields">
              <div>
                <label htmlFor="device-id">Display ID</label>
                <input
                  id="device-id"
                  value={deviceId}
                  onChange={(event) => setDeviceId(event.target.value)}
                  required
                />
              </div>
              <div>
                <label htmlFor="pairing-code">Pairing code</label>
                <input
                  id="pairing-code"
                  className="code-input"
                  value={pairingCode}
                  onChange={(event) => setPairingCode(event.target.value.toUpperCase())}
                  placeholder="SKY281"
                  required
                />
              </div>
            </div>

            <label htmlFor="setup-address">Window location</label>
            <input
              id="setup-address"
              value={address}
              onChange={(event) => setAddress(event.target.value)}
              placeholder="Address or postcode"
              required
            />

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
                        onClick={() => setBearing(direction.bearing)}
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
                  onChange={(event) => setBearing(Number(event.target.value))}
                />

                <label htmlFor="field-of-view">Visible width: {fieldOfView}°</label>
                <input
                  id="field-of-view"
                  type="range"
                  min="20"
                  max="180"
                  step="5"
                  value={fieldOfView}
                  onChange={(event) => setFieldOfView(Number(event.target.value))}
                />

                <label htmlFor="view-distance">Clear viewing distance: {maxDistance} km</label>
                <input
                  id="view-distance"
                  type="range"
                  min="1"
                  max="50"
                  value={maxDistance}
                  onChange={(event) => setMaxDistance(Number(event.target.value))}
                />
              </div>

              <div className="viewing-diagram" aria-label="Top-down preview of the viewing zone">
                <svg viewBox="0 0 240 160" role="img">
                  <title>Window viewing direction and field of view</title>
                  <path d={sectorPath} className="viewing-sector" />
                  <circle cx="120" cy="132" r="9" className="observer" />
                  <line x1="120" y1="8" x2="120" y2="20" className="north-marker" />
                  <text x="120" y="7" textAnchor="middle">N</text>
                </svg>
                <strong>{bearing}° · {fieldOfView}° view</strong>
                <span>Up to {maxDistance} km from this window</span>
              </div>
            </div>

            <button type="submit" className="primary-action" disabled={saving}>
              {saving ? 'Pairing display…' : 'Save view and pair display'}
            </button>
          </form>
        )}

        {step === 'complete' && (
          <div className="setup-complete">
            <span className="complete-mark" aria-hidden="true">✓</span>
            <span className="step-number">03</span>
            <h2>Your display is ready.</h2>
            <p>
              The pairing screen will clear on its next check and the display will
              start looking through your configured window.
            </p>
            <Link to="/" className="primary-action">Open your window view</Link>
          </div>
        )}
      </section>
    </div>
  );
}
