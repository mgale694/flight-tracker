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
