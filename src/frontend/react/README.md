# Flight Tracker React Frontend

This is a plain React JavaScript implementation of the Flight Tracker frontend, designed to run without any build tools.

## Features

- **No Build Step Required**: Uses React and Babel via CDN with in-browser JSX transformation
- **Real-time Flight Tracking**: Displays live flight data from the backend API
- **Waveshare E-ink Simulation**: Simulates the Raspberry Pi e-ink display
- **Airport-style Flight Board**: Shows flight departures like an airport board
- **Activity Console**: Real-time logs and monitoring
- **Settings Management**: Configure tracking parameters
- **Dark/Light Theme**: Toggle between themes with persistence

## Structure

```
src/frontend/react/
├── index.html          # Main HTML file with React CDN setup
├── styles.css          # Complete CSS styling
├── api.js             # API client for backend communication
├── App.js             # Main application component
├── components/
│   ├── ThemeSwitch.js      # Theme toggle component
│   ├── FlightBoard.js      # Airport-style flight board
│   ├── WaveshareDisplay.js # E-ink display simulation
│   ├── Display.js          # Display components
│   └── Settings.js         # Settings form
└── pages/
    ├── Tracker.js          # Main tracking page
    └── Activities.js       # Activity console page
```

## How to Run

1. **Start the Backend**: Make sure the Python backend is running on port 8000

   ```bash
   cd src/backend
   python main.py
   ```

2. **Serve the Frontend**: Use any static file server

   ```bash
   # Using Python's built-in server
   cd src/frontend/react
   python -m http.server 3000

   # Or using Node.js serve
   npx serve . -p 3000

   # Or any other static file server
   ```

3. **Open in Browser**: Navigate to `http://localhost:3000`

## Architecture

### No Build Tools

- React 18 loaded via CDN
- Babel Standalone for JSX transformation in the browser
- All components written as plain JavaScript functions
- No webpack, vite, or other bundlers required

### State Management

- Uses React hooks (`useState`, `useEffect`) for component state
- No external state management library
- Local storage for theme and log persistence

### API Communication

- Fetch API for HTTP requests
- Automatic base URL detection (localhost vs network IP)
- Error handling and connection status tracking

### Component Architecture

- Functional components using React.createElement
- Components exported to global window object
- Modular design matching the original TypeScript version

### Styling

- CSS Custom Properties for theming
- Responsive design with media queries
- Material Icons via Google Fonts CDN
- Dark/light theme support

## API Endpoints

The frontend communicates with these backend endpoints:

- `GET /flights` - Get current flight data
- `GET /config` - Get configuration
- `POST /config` - Update configuration
- `GET /health` - Health check
- `GET /logs` - Get activity logs
- `DELETE /logs` - Clear activity logs

## Features

### Flight Tracker Page

- Real-time flight data display
- Waveshare e-ink display simulation
- Flight board with departures
- Automatic flight rotation every 10 seconds
- Connection status indicators

### Activity Console

- Real-time activity logs
- Log filtering by level (info, warning, error, etc.)
- Search functionality
- Export logs to file
- Clear logs functionality

### Settings

- Configure tracking address
- Set search radius
- Adjust max flights and session time
- Save configuration to backend

### Theme System

- Light and dark theme support
- Automatic system preference detection
- Theme persistence in localStorage
- CSS custom properties for easy customization

## Browser Compatibility

Requires a modern browser with support for:

- ES6+ features (arrow functions, destructuring, etc.)
- Fetch API
- CSS Custom Properties
- React 18

## Development

To modify the frontend:

1. Edit the relevant `.js` files
2. Refresh the browser (no build step needed)
3. Components are automatically re-evaluated

For debugging:

- Use browser dev tools
- Console.log statements work normally
- React Developer Tools can be used

## Deployment

For production deployment:

1. Copy all files to your web server
2. Ensure the backend is accessible
3. Update API base URL if needed in `api.js`
4. Serve files with proper MIME types

The frontend is completely static and can be served from any web server, CDN, or even opened directly as files in the browser (with CORS considerations for API calls).
