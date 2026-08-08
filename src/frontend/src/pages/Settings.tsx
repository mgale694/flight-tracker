/**
 * Settings page - Configuration management
 */

import SettingsComponent from '../components/Settings';
import './Settings.css';

export default function Settings() {
  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>Settings</h1>
        <p className="settings-subtitle">Tune the sky outside your window and the e-paper layout.</p>
      </div>
      
      <div className="settings-content">
        <SettingsComponent />
        
        <div className="settings-help">
          <h3>Location</h3>
          <ul>
            <li><strong>Address formats:</strong> Enter any recognizable address, postcode, or place name</li>
            <li><strong>Direction:</strong> Point the cone where the window faces</li>
            <li><strong>Distance:</strong> Choose how far you can clearly see from that window</li>
          </ul>
          
          <h3>Display</h3>
          <ul>
            <li><strong>Fields:</strong> Use each dropdown to choose an e-paper line</li>
            <li><strong>Order:</strong> Move lines with the arrow buttons—no dragging required</li>
          </ul>
          
          <h3>After saving</h3>
          <p>Changes take effect immediately. Go to the Tracker page to see flights at your new location.</p>
        </div>
      </div>
    </div>
  );
}
