# Flight Tracker Frontend

React TypeScript frontend that emulates the Raspberry Pi e-ink display and provides a settings interface.

## Features

- Accurate e-ink display emulation
- Boot sequence animation
- Real-time flight tracking display
- Settings page for configuration
- WebSocket integration for live updates
- Responsive design with display scaling

## Installation

1. Install dependencies:

```bash
npm install
```

2. Run the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Components

- **Display Components**: Emulate the Raspberry Pi e-ink display
- **Tracker Page**: Main flight tracking interface
- **Settings Page**: Configuration management
- **WebSocket Integration**: Real-time updates from backend

## Display Emulation

The frontend accurately replicates the 250x122 pixel e-ink display used on the Raspberry Pi, including:

- Boot screen with random face and phrase
- Flight information display with exact layout
- Monospace font styling
- Black and white color scheme
- Responsive scaling for different screen sizes

## Development

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## Configuration

The frontend connects to the backend API at `http://localhost:8000` by default. Modify the `API_BASE` constant in `src/api.ts` to change this.
