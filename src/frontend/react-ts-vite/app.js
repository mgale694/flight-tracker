// Flight Tracker JavaScript - Simple and Functional

// Global variables
let backendUrl = 'http://localhost:8000';

// Initialize the app when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Set initial backend URL from window location
    const currentHost = window.location.hostname;
    if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
        backendUrl = `http://${currentHost}:8000`;
        document.getElementById('backend-url').value = backendUrl;
    }
    
    // Check backend connection on startup
    checkBackendConnection();
    
    // Load initial activities
    loadActivities();
    
    // Set up event listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Enter key support for search inputs
    document.getElementById('flight-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchFlight();
        }
    });
    
    document.getElementById('location-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchByLocation();
        }
    });
}

// Tab functionality
function showTab(tabName) {
    // Hide all tab contents
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Backend connection check
async function checkBackendConnection() {
    const statusElement = document.getElementById('backend-status');
    const indicator = document.getElementById('status-indicator');
    
    try {
        statusElement.textContent = 'Checking backend...';
        indicator.className = 'status-indicator';
        
        const response = await fetch(`${backendUrl}/health`);
        if (response.ok) {
            const data = await response.json();
            statusElement.textContent = 'Backend Online';
            indicator.className = 'status-indicator online';
        } else {
            throw new Error('Backend responded with error');
        }
    } catch (error) {
        statusElement.textContent = 'Backend Offline';
        indicator.className = 'status-indicator offline';
        console.error('Backend connection failed:', error);
    }
}

// Flight search functionality
async function searchFlight() {
    const flightInput = document.getElementById('flight-input');
    const flightNumber = flightInput.value.trim();
    
    if (!flightNumber) {
        showError('Please enter a flight number');
        return;
    }
    
    const resultsContainer = document.getElementById('flight-results');
    resultsContainer.innerHTML = '<div class="loading">Searching for flight information...</div>';
    
    try {
        const response = await fetch(`${backendUrl}/flights?flight=${encodeURIComponent(flightNumber)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        displayFlightResults(data, resultsContainer);
        
    } catch (error) {
        console.error('Flight search error:', error);
        resultsContainer.innerHTML = `<div class="error">Failed to search flights: ${error.message}</div>`;
    }
}

// Location search functionality
async function searchByLocation() {
    const locationInput = document.getElementById('location-input');
    const location = locationInput.value.trim();
    
    if (!location) {
        showError('Please enter a location');
        return;
    }
    
    const resultsContainer = document.getElementById('flight-results');
    resultsContainer.innerHTML = '<div class="loading">Searching flights by location...</div>';
    
    try {
        const response = await fetch(`${backendUrl}/flights?location=${encodeURIComponent(location)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        displayFlightResults(data, resultsContainer);
        
    } catch (error) {
        console.error('Location search error:', error);
        resultsContainer.innerHTML = `<div class="error">Failed to search by location: ${error.message}</div>`;
    }
}

// Display flight results
function displayFlightResults(data, container) {
    if (!data || (Array.isArray(data) && data.length === 0)) {
        container.innerHTML = '<div class="error">No flights found</div>';
        return;
    }
    
    // Handle both single flight and array of flights
    const flights = Array.isArray(data) ? data : [data];
    
    let html = '';
    flights.forEach(flight => {
        html += createFlightCard(flight);
    });
    
    container.innerHTML = html || '<div class="error">No flight data available</div>';
}

// Create HTML for a flight card
function createFlightCard(flight) {
    const flightNumber = flight.flight_number || flight.callsign || 'Unknown';
    const airline = flight.airline || 'Unknown Airline';
    const status = flight.status || 'Unknown';
    
    return `
        <div class="flight-card">
            <h4>${flightNumber} - ${airline}</h4>
            <div class="flight-info">
                <div class="info-item">
                    <span class="info-label">Status</span>
                    <span class="info-value">${status}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Origin</span>
                    <span class="info-value">${flight.origin || 'Unknown'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Destination</span>
                    <span class="info-value">${flight.destination || 'Unknown'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Departure Time</span>
                    <span class="info-value">${flight.departure_time || 'Unknown'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Arrival Time</span>
                    <span class="info-value">${flight.arrival_time || 'Unknown'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Aircraft</span>
                    <span class="info-value">${flight.aircraft || 'Unknown'}</span>
                </div>
            </div>
        </div>
    `;
}

// Load activities
async function loadActivities() {
    const activitiesContainer = document.getElementById('activities-list');
    activitiesContainer.innerHTML = '<div class="loading">Loading activities...</div>';
    
    try {
        const response = await fetch(`${backendUrl}/activities`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        displayActivities(data, activitiesContainer);
        
    } catch (error) {
        console.error('Activities load error:', error);
        activitiesContainer.innerHTML = `<div class="error">Failed to load activities: ${error.message}</div>`;
    }
}

// Display activities
function displayActivities(data, container) {
    if (!data || !Array.isArray(data) || data.length === 0) {
        container.innerHTML = '<div class="loading">No activities found</div>';
        return;
    }
    
    let html = '';
    data.forEach(activity => {
        html += `
            <div class="activity-item">
                <div class="activity-time">${formatDateTime(activity.timestamp)}</div>
                <div class="activity-message">${activity.message}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Settings functions
function updateBackendUrl() {
    const input = document.getElementById('backend-url');
    backendUrl = input.value.trim();
    
    if (!backendUrl.startsWith('http')) {
        backendUrl = 'http://' + backendUrl;
        input.value = backendUrl;
    }
    
    showSuccess('Backend URL updated');
    checkBackendConnection();
}

function testConnection() {
    checkBackendConnection();
}

// Utility functions
function formatDateTime(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleString();
    } catch (error) {
        return timestamp;
    }
}

function showError(message) {
    console.error(message);
    // You could add a toast notification here
}

function showSuccess(message) {
    console.log(message);
    // You could add a toast notification here
}

// Refresh data periodically
setInterval(() => {
    checkBackendConnection();
}, 30000); // Check every 30 seconds
