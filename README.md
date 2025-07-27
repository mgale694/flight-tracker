# Flight Tracker

A real-time aircraft tracking system built for Raspberry Pi with a modern web interface. This project tracks aircraft overhead using the FlightRadar24 API and displays information on both an e-ink display and a web dashboard.

## 🚀 Features

- **Real-time Flight Tracking**: Monitor aircraft in your area using FlightRadar24 data
- **Raspberry Pi Display**: E-ink display showing current flights overhead
- **Web Dashboard**: Modern React-based interface with:
  - Live flight display simulation
  - Flight departure board
  - Settings management
  - Activity logging
  - Dark/light theme support
- **Backend API**: FastAPI-based service with configurable tracking parameters
- **Multi-platform**: Runs on Raspberry Pi and standard computers

## 📁 Project Structure

```
flight-tracker/
├── docs/                    # Documentation and guides
├── src/                     # Source code
│   ├── backend/            # FastAPI backend service
│   ├── frontend/           # React web interface
│   └── raspi/              # Raspberry Pi specific code
├── scripts/                # Utility scripts
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd src/backend
pip install -r requirements.txt
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

```bash
cd src/frontend/react
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`

### Raspberry Pi Setup

```bash
cd src/raspi
# Install hardware-specific dependencies
pip install -r requirements.txt
# Configure display in config.toml
python tracker.py
```

## 🔧 Configuration

Configuration is managed through TOML files:

- **Backend**: `src/backend/config.toml` - API settings, tracking parameters
- **Raspberry Pi**: `src/raspi/config.toml` - Hardware display settings

Key configuration options:

- `address`: Location for flight tracking
- `search_radius_meters`: Tracking radius in meters
- `max_flights`: Maximum number of flights to track
- Display settings for various e-ink displays

## 📱 Usage

1. **Web Interface**: Access the React dashboard at `http://localhost:5173`

   - View live flight simulations
   - Monitor flight departure board
   - Adjust tracking settings
   - View activity logs

2. **Raspberry Pi Display**: The e-ink display shows:

   - Current flight callsign and details
   - Flight count and session timer
   - Route information and aircraft data

3. **API Access**: The backend provides RESTful endpoints:
   - `GET /flights` - Current tracked flights
   - `GET /config` - Current configuration
   - `POST /config` - Update settings
   - `GET /logs` - Activity logs

## 🏗️ Architecture

- **Backend**: FastAPI with asynchronous flight data fetching
- **Frontend**: React with TypeScript, Vite build system
- **Hardware**: Supports multiple e-ink display types
- **Data**: FlightRadar24 API integration with local caching
- **Persistence**: localStorage for frontend state, in-memory for backend logs

## 📚 Documentation

See the `docs/` folder for detailed guides:

- [Polling Guide](docs/POLLING_GUIDE.md) - API polling patterns
- [Setup Instructions](docs/) - Detailed installation steps
- [Hardware Guide](docs/) - Raspberry Pi and display setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.

## 🛠️ Development

### Backend Development

```bash
cd src/backend
python main.py --host 127.0.0.1 --port 8000
```

### Frontend Development

```bash
cd src/frontend/react
npm run dev
```

### Raspberry Pi Testing

```bash
cd src/raspi
python tracker.py --debug
```

## 🆘 Troubleshooting

- **Connection Issues**: Check backend URL in frontend configuration
- **No Flights Detected**: Verify location and radius settings
- **Display Problems**: Check hardware connections and display type configuration
- **API Errors**: Ensure FlightRadar24 API access is working

## 📈 Roadmap

- [ ] Multiple location tracking
- [ ] Historical flight data
- [ ] Email/push notifications
- [ ] Mobile app
- [ ] Weather integration
- [ ] Flight path mapping

---

Built with ❤️ for aviation enthusiasts and Raspberry Pi makers

- React frontend on http://localhost:5173

### Manual Setup

#### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Raspberry Pi

```bash
python raspi_main.py
```

# Flight Tracker Application

This project is a Streamlit application that allows users to track flights based on their selected direction. The application fetches flight data and displays relevant information about flights overhead in real-time.

## Project Structure

```
├── src
│   ├── app.py                # Main entry point of the Streamlit application
│   ├── components
│   │   └── __init__.py       # Reusable components for the Streamlit application
│   └── utils
│       └── __init__.py       # Utility functions for fetching and processing flight data
├── requirements.txt           # Project dependencies
└── README.md                  # Documentation for the project
```

## Setup Instructions

1. Clone the repository:

   ```
   git clone <repository-url>
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```
   streamlit run src/app.py
   ```

## Usage Guidelines

- Upon running the application, users can select a direction (e.g., North, South, East, West) for flight tracking.
- The application will display flight information for flights currently overhead based on the selected direction.
- The information includes flight callsigns, origin and destination airports, and the current time of tracking.

## Application Screenshots

### 1. User Input Flow

![User Input Flow](docs/img/meta.png)

_The user enters their address/postcode, checks and confirms the location, then selects direction and search radius._

### 2. Map Display

![Map Display](docs/img/map.png)

_The app displays the real location, search center, and search radius on an interactive map._

### 3. Flights Display

![Flights Display](docs/img/flights.png)

_Flight information is shown using metrics for each flight overhead, including callsign, route, and time._

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.
