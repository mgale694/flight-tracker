/**
 * Settings page - Configuration management
 */

import SettingsComponent from '../components/Settings';
import './Settings.css';

export default function Settings() {
  const handleConfigUpdate = () => {
    // Optionally show a notification or trigger a refresh
    console.log('Configuration updated successfully');
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>Settings</h1>
        <p className="settings-subtitle">Configure your flight tracking preferences</p>
      </div>
      
      <div className="settings-content">
        <SettingsComponent onConfigUpdate={handleConfigUpdate} />
        
        <div className="settings-help">
          <h3>📍 Location Tips</h3>
          <ul>
            <li><strong>Address formats:</strong> Enter any recognizable address, postcode, or place name</li>
            <li><strong>Examples:</strong> "123 Main St, London, UK", "SW1A 1AA", "Heathrow Airport"</li>
            <li><strong>Radius:</strong> Set higher for airports (15-50km), lower for residential areas (3-10km)</li>
            <li><strong>Max flights:</strong> More flights = more data but slower updates</li>
          </ul>
          
          <h3>🖥️ Display Settings</h3>
          <ul>
            <li><strong>Hold Time:</strong> Keeps the last flight on display even after it leaves the area</li>
            <li><strong>Recommended:</strong> 30-60 seconds to avoid blank screens between flights</li>
          </ul>
          
          <h3>🔄 After Saving</h3>
          <p>Changes take effect immediately. Go to the Tracker page to see flights at your new location.</p>
        </div>
      </div>
    </div>
  );
}
