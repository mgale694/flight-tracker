import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import ViewingZoneEditor from '../components/ViewingZoneEditor';
import type { LocationPreview } from '../types';
import './Setup.css';

type SetupStep = 'account' | 'window' | 'complete';

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
  const [locationPreview, setLocationPreview] = useState<LocationPreview | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      const resolvedLocation = await api.previewLocation(address.trim());
      setLocationPreview(resolvedLocation);
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

            <label htmlFor="setup-address">Full window address</label>
            <input
              id="setup-address"
              autoComplete="street-address"
              value={address}
              onChange={(event) => {
                setAddress(event.target.value);
                setLocationPreview(null);
              }}
              onBlur={() => {
                if (address.trim().length >= 3) {
                  void api.previewLocation(address.trim())
                    .then(setLocationPreview)
                    .catch(() => undefined);
                }
              }}
              placeholder="10 Downing Street, London, SW1A 2AA"
              required
            />

            <ViewingZoneEditor
              bearing={bearing}
              fieldOfView={fieldOfView}
              maxDistance={maxDistance}
              location={locationPreview}
              onBearingChange={setBearing}
              onFieldOfViewChange={setFieldOfView}
              onMaxDistanceChange={setMaxDistance}
            />

            <button type="submit" className="primary-action" disabled={saving}>
              {saving ? 'Pairing display…' : 'Save view and pair display'}
            </button>
          </form>
        )}

        {step === 'complete' && (
          <div className="setup-complete">
            <span className="complete-mark">Complete</span>
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
