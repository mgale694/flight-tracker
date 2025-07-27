// Smart API base URL detection
function getApiBaseUrl() {
  // Get current window location
  const currentHost = window.location.hostname;
  
  // If accessing via network IP, use the same IP for backend
  if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
    return `http://${currentHost}:8000`;
  }
  
  // Default to localhost
  return 'http://localhost:8000';
}

const API_BASE = getApiBaseUrl();

window.FlightTrackerAPI = {
  // Main endpoint - gets current flights (simplified)
  async getFlights() {
    const response = await fetch(`${API_BASE}/flights`);
    if (!response.ok) throw new Error('Failed to fetch flights');
    return response.json();
  },

  // Config management
  async getConfig() {
    const response = await fetch(`${API_BASE}/config`);
    if (!response.ok) throw new Error('Failed to fetch config');
    const data = await response.json();
    return data.main;
  },

  async updateConfig(config) {
    const response = await fetch(`${API_BASE}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to update config');
  },

  // Health check
  async getHealth() {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Failed to fetch health status');
    return response.json();
  },

  // Mock boot data for compatibility (since simplified backend doesn't have this)
  async getBootData() {
    const faces = ["(⌐■_■)", "(╯°□°）╯", "ಠ_ಠ", "(◕‿◕)", "¯\\_(ツ)_/¯"];
    const phrases = [
      "Booting up flight tracker...",
      "Scanning the skies...", 
      "Ready for takeoff!",
      "Aircraft detection online",
      "Flight radar activated"
    ];
    
    return {
      face: faces[Math.floor(Math.random() * faces.length)],
      phrase: phrases[Math.floor(Math.random() * phrases.length)],
      message: "Flight Tracker initialized"
    };
  },

  // Activity logs
  async getActivityLogs() {
    const response = await fetch(`${API_BASE}/logs`);
    if (!response.ok) throw new Error('Failed to fetch activity logs');
    return response.json();
  },

  // Clear activity logs
  async clearActivityLogs() {
    const response = await fetch(`${API_BASE}/logs`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to clear activity logs');
    return response.json();
  }
};
