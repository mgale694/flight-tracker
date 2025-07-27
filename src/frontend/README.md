# Frontend - React Web Dashboard

Modern React-based web interface for the Flight Tracker system, providing a comprehensive dashboard for monitoring aircraft and managing the tracking system.

## 🚀 Features

- **Real-time Flight Display**: Accurate simulation of the Raspberry Pi e-ink display
- **Flight Departure Board**: Interactive board showing flight history and status
- **Settings Management**: Configure tracking parameters via web interface
- **Activity Console**: View and manage system logs and events
- **Theme Support**: Dark/light mode toggle with system preference detection
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 📁 Directory Structure

```
frontend/
├── react/                 # Main React application
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── pages/         # Page components (Display, Settings, Activities)
│   │   ├── api.ts         # Backend API integration
│   │   ├── types.ts       # TypeScript type definitions
│   │   └── theme.ts       # Theme management utilities
│   ├── package.json       # Dependencies and scripts
│   └── vite.config.ts     # Vite configuration
└── stremlit/             # Legacy Streamlit prototype (deprecated)
```

## 🛠️ Installation & Setup

### Prerequisites

- Node.js 16+ and npm (or yarn)
- Running backend service on `http://localhost:8000`

### Install Dependencies

```bash
cd src/frontend/react
npm install
```

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Production Build

```bash
npm run build
npm run preview
```

## 🎨 Key Components

### Display Page (`pages/Tracker.tsx`)

- **WaveshareDisplay**: Pixel-perfect e-ink display simulation
- **FlightBoard**: Real-time departure board with flight history
- **Connection Status**: Backend connectivity monitoring
- **Rotation System**: Automatic cycling through detected flights

### Settings Page (`pages/Settings.tsx`)

- **Location Configuration**: Address and search radius settings
- **Flight Limits**: Maximum flights and session time controls
- **Real-time Updates**: Settings sync with backend immediately
- **Validation**: Input validation and error handling

### Activities Page (`pages/Activities.tsx`)

- **Log Console**: Terminal-style activity log viewer
- **Filtering**: Filter by log level and search functionality
- **Real-time Updates**: Auto-refresh backend logs every 5 seconds
- **Export**: Download logs as text files
- **Log Management**: Clear logs from both frontend and backend

### Theme System (`theme.ts`)

- **CSS Custom Properties**: Centralized color and spacing system
- **Dark/Light Modes**: Comprehensive theme switching
- **System Preference**: Automatic detection of OS theme preference
- **Persistent Settings**: Theme choice saved to localStorage

## 🔌 API Integration

### FlightTrackerAPI Class (`api.ts`)

Handles all backend communication:

```typescript
// Get current flights
const response = await FlightTrackerAPI.getFlights();

// Update configuration
await FlightTrackerAPI.updateConfig(newConfig);

// Fetch activity logs
const logs = await FlightTrackerAPI.getActivityLogs();
```

### Smart Base URL Detection

Automatically detects the correct backend URL:

- Development: `http://localhost:8000`
- Network access: Uses current hostname with port 8000
- Environment override: `VITE_API_BASE_URL`

## 🎯 State Management

### React State Patterns

- **Local State**: Component-specific state with `useState`
- **Effect Hooks**: Data fetching and cleanup with `useEffect`
- **Refs**: DOM manipulation and interval management with `useRef`

### Data Flow

```
Backend API → Frontend State → Component Rendering → User Interaction → API Updates
```

### Polling Strategy

- **Flight Data**: 5-second intervals for real-time updates
- **Activity Logs**: 5-second intervals for log synchronization
- **Health Checks**: Integrated with flight polling for connectivity status

## 🎨 Styling Architecture

### CSS Custom Properties

Centralized design system using CSS variables:

```css
:root {
  --primary-color: #007acc;
  --bg-primary: #ffffff;
  --text-primary: #333333;
  /* ... */
}

[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: #ffffff;
  /* ... */
}
```

### Component Styles

- **Modular CSS**: Each component has its own stylesheet
- **BEM Methodology**: Consistent naming conventions
- **Responsive Design**: Mobile-first approach with breakpoints

### Theme Implementation

- **Automatic Switching**: JavaScript-based theme application
- **Smooth Transitions**: CSS transitions for theme changes
- **System Integration**: Respects OS dark mode preference

## 📱 Responsive Design

### Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Adaptive Features

- **Navigation**: Collapsible mobile menu
- **Display**: Responsive e-ink display scaling
- **Tables**: Horizontal scrolling on mobile
- **Controls**: Touch-friendly button sizing

## 🔧 Development Tools

### Vite Configuration

- **Fast HMR**: Hot module replacement for rapid development
- **TypeScript**: Full TypeScript support with type checking
- **CSS Processing**: PostCSS with autoprefixer
- **Build Optimization**: Tree shaking and code splitting

### TypeScript Integration

- **Strict Mode**: Enhanced type safety
- **API Types**: Shared types for backend communication
- **Component Props**: Fully typed React components

### ESLint Configuration

- **Code Quality**: Consistent code style enforcement
- **React Rules**: React-specific linting rules
- **Accessibility**: a11y linting for better accessibility

## 🧪 Testing & Quality

### Development Workflow

```bash
# Start development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

### Browser Compatibility

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+
- **ES2020**: Modern JavaScript features
- **CSS Grid/Flexbox**: Modern layout systems

## 🚀 Deployment

### Production Build

```bash
npm run build
# Outputs to dist/ directory
```

### Serving Static Files

The built application can be served by any static file server:

- **Nginx**: Traditional web server
- **Netlify/Vercel**: JAMstack platforms
- **Express**: Node.js static serving

### Environment Configuration

```bash
# .env file
VITE_API_BASE_URL=http://your-backend-url:8000
```
