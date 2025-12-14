# Flight Tracker Frontend

React + TypeScript + Vite web dashboard for monitoring and configuring the flight tracker system.

## Features

- **Real-time Flight Tracking**: Live updates of detected aircraft
- **E-ink Display Simulator**: Visual representation of Waveshare 2.13" display
- **Flight Board**: Detailed table view of all detected flights
- **Activity Logs**: Real-time system activity monitoring
- **Theme System**: Light, dark, and auto modes with localStorage persistence
- **Responsive Design**: Works on desktop and mobile devices

## Requirements

- Node.js 18+ and npm
- Backend API running on http://localhost:8000 (or configured URL)

## Installation

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Configure API URL** (optional):
   Create a `.env` file in this directory:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

## Usage

### Development Server

**Start the dev server** (with hot reload):

```bash
npm run dev
```

The app will be available at:

- Local: `http://localhost:5173`
- Network: `http://<your-ip>:5173`

**Or use the script**:

```bash
../../scripts/start-frontend.sh
```

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── main.tsx                 # Application entry point
├── App.tsx                  # Main app with routing
├── App.css                  # App-level styles
├── index.css                # Global styles & theme variables
│
├── api.ts                   # Backend API client
├── types.ts                 # TypeScript type definitions
├── theme.ts                 # Theme management system
│
├── components/              # Reusable components
│   ├── ThemeSwitch.tsx     # Theme toggle component
│   ├── WaveshareDisplay.tsx # E-ink display simulator
│   ├── FlightBoard.tsx     # Flight table component
│   ├── Settings.tsx        # Configuration form
│   └── *.css               # Component-specific styles
│
└── pages/                   # Page components
    ├── Tracker.tsx         # Main tracker page
    ├── Activities.tsx      # Activity logs page
    └── *.css               # Page-specific styles
```

## Pages

### Tracker Page (`/`)

The main dashboard showing:

- **E-ink Display Simulator**: Mimics the Waveshare 2.13" display (250x122px)
  - Shows one flight at a time
  - Rotates through detected flights every 5 seconds
  - Displays scan screen when no flights detected
  - Shows session statistics
- **Flight Board**: Table view of all detected flights with sortable columns
- **Settings Panel**: Update tracking configuration
  - Location address
  - Search radius
  - Maximum flights
- **Session Statistics**: Flights detected, unique aircraft, session duration

### Activities Page (`/activities`)

Real-time activity log viewer with:

- **Auto-refresh**: Toggle automatic updates (every 3 seconds)
- **Category Filter**: Filter by SYSTEM, RADAR, FLIGHT, CONFIG, ERROR, INFO
- **Detailed View**: Expandable details for each activity
- **Clear Logs**: Button to clear all activities
- **Color Coding**: Visual category identification

## Features

### Theme System

Three theme modes:

- **Light**: Traditional light theme
- **Dark**: Traditional dark theme
- **Auto**: Follows system preferences

Theme preference is saved in localStorage and persists across sessions.

### Real-time Updates

- **Flight Data**: Polls backend every 5 seconds
- **Activity Logs**: Polls backend every 3 seconds (when auto-refresh enabled)
- **Display Rotation**: Cycles through flights every 5 seconds

### E-ink Display Simulator

Accurately simulates the Waveshare 2.13" V4 display:

- **Resolution**: 250x122 pixels
- **Aspect Ratio**: Preserved
- **Monochrome**: Black and white only
- **Content**: Matches actual e-ink display layout

## API Integration

The frontend communicates with the backend API:

### Endpoints Used

- `GET /api/flights` - Get current flights
- `GET /api/config` - Get configuration
- `PUT /api/config` - Update configuration
- `GET /api/activities` - Get activity logs
- `DELETE /api/activities` - Clear activity logs
- `GET /api/health` - Health check

### API Client

Located in `src/api.ts`, provides typed methods for all backend endpoints:

```typescript
import { api } from "./api";

// Get flights
const flights = await api.getFlights();

// Update config
await api.updateConfig({
  address: "New York, NY",
  search_radius_meters: 5000,
});

// Get activities
const activities = await api.getActivities(100, "FLIGHT");
```

## Development

### TypeScript

Full TypeScript support with strict type checking. All API responses and component props are typed.

### Component Structure

Components follow a consistent structure:

1. Interface definitions
2. Component function
3. JSX return
4. Default export

### Styling

- **Global styles**: `index.css` with CSS custom properties for theming
- **Component styles**: Scoped CSS files alongside components
- **Theme variables**: All colors use CSS custom properties
- **Responsive**: Mobile-first approach with media queries

### Best Practices

- Use TypeScript interfaces for all props
- Include error handling in all API calls
- Show loading states during async operations
- Provide user feedback for actions
- Keep components focused and reusable

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Backend API URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

### Vite Configuration

Edit `vite.config.ts` to customize:

- Port number
- Proxy settings
- Build options

Example:

```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
```

## Troubleshooting

### Backend Connection Issues

**Error**: "Failed to fetch flights"

**Solutions**:

- Verify backend is running on port 8000
- Check `VITE_API_URL` environment variable
- Check browser console for CORS errors
- Ensure backend CORS is configured correctly

### No Flights Displaying

**Solutions**:

- Check backend configuration (address, radius)
- Verify FlightRadar24 API is working
- Check Activity Logs for error messages
- Increase search radius in Settings

### Theme Not Persisting

**Solutions**:

- Check browser localStorage is enabled
- Clear browser cache
- Check for JavaScript errors in console

### Display Simulator Not Showing Flights

**Solutions**:

- Ensure flights array is not empty
- Check that rotation interval is running
- Verify flight data format matches interface
- Check browser console for errors

## Performance

### Optimizations

- **Polling Intervals**: Reasonable intervals to avoid excessive API calls
- **React Memoization**: Key components use proper key props
- **CSS Animations**: GPU-accelerated transforms
- **Bundle Size**: Code splitting with React Router

### Recommendations

- Backend caching reduces redundant API calls
- Adjust polling intervals based on needs
- Use production build for deployment
- Enable gzip compression on server

## Technologies

- **React 19**: Latest React version with new features
- **TypeScript 5.9**: Full type safety
- **Vite 7**: Fast build tool and dev server
- **React Router 7**: Client-side routing
- **CSS Custom Properties**: Theme system
- **Fetch API**: HTTP requests

## Deployment

### Production Build

```bash
npm run build
```

### Serve Static Files

Use any static file server:

```bash
# Using serve
npx serve dist

# Using nginx
# Copy dist/ contents to nginx html directory

# Using Vercel/Netlify
# Connect repository and deploy
```

### Environment Variables

Set `VITE_API_URL` in your deployment platform to point to your production backend.

## License

See root LICENSE file.

## Support

For issues or questions:

- Check Activity Logs for error messages
- Verify backend API is accessible
- Check browser console for JavaScript errors
- Ensure all dependencies are installed
