# ✈️ Flight Tracker

Real-time aircraft tracking system with web dashboard and e-ink display support.

![Flight Tracker](https://img.shields.io/badge/Python-3.11%2B-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🛫 **Real-time flight tracking** using FlightRadar24 API
- 🌐 **Web dashboard** with live updates and flight details
- 🖥️ **E-ink display** support for Raspberry Pi (Waveshare 2.13" V4)
- 📍 **Location-based** search with configurable radius
- ⚙️ **Web-based settings** for easy configuration
- 📊 **Activity logging** to track detection history
- 🎨 **Dark/Light mode** with system preference detection

## Quick Start

### Desktop Development

```bash
# Start backend and frontend together
./scripts/start-flight-tracker.sh
```

Access at: `http://localhost:5173`

### Raspberry Pi (Complete System)

```bash
# One command to start everything
./scripts/start-raspi-all.sh
```

Access from any device on your network: `http://<pi-ip>:5173`

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Flight Tracker                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐      ┌──────────────┐       │
│  │   Backend    │◄────►│   Frontend   │       │
│  │   FastAPI    │      │  React + TS  │       │
│  │  Port 8000   │      │  Port 5173   │       │
│  └──────────────┘      └──────────────┘       │
│         │                                       │
│         ▼                                       │
│  ┌──────────────┐      ┌──────────────┐       │
│  │ FlightRadar  │      │  Raspberry   │       │
│  │     API      │      │  Pi Display  │       │
│  └──────────────┘      └──────────────┘       │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Components

### Backend (Python/FastAPI)

- Flight data from FlightRadar24
- Location-based filtering
- Configuration management
- Activity logging
- RESTful API

### Frontend (React/TypeScript)

- Real-time flight dashboard
- E-ink display simulator
- Settings interface
- Activity history
- Dark/light theme

### Raspberry Pi Client (Python)

- E-ink display driver (Waveshare 2.13" V4)
- Boot animations
- Flight rendering
- Hardware abstraction

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started quickly
- **[RASPI_SETUP.md](RASPI_SETUP.md)** - Raspberry Pi setup guide
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and fixes
- **[docs/](docs/)** - Architecture and development docs

## Requirements

### Desktop Development

- Python 3.11+
- Node.js 18+
- Internet connection

### Raspberry Pi

- Raspberry Pi (any model with GPIO)
- Python 3.11+
- Node.js 18+
- Waveshare 2.13" V4 e-ink display (optional)
- Internet connection

## License

MIT License - See [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please read the docs and feel free to submit PRs.
