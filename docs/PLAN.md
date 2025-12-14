# Flight Tracker - Development Plan

**Project Goal**: Build a complete flight tracking system with backend API, web frontend, and Raspberry Pi e-ink display client.

**Date Created**: 14 December 2025  
**Status**: Phase 3 Complete - Raspberry Pi Client Ready! ✅✅✅

---

## Project Structure

```
flight-tracker/
├── src/
│   ├── backend/          # FastAPI flight tracking API
│   ├── frontend/         # React + TypeScript web interface
│   └── raspi/           # Raspberry Pi e-ink display client
├── scripts/             # Utility scripts and startup scripts
├── docs/               # Documentation
└── requirements.txt    # Root dependencies
```

---

## Phase 1: Backend API (Core Foundation)

**Priority**: HIGH - This is the foundation for everything else

### Tasks

- [x] **1.1 Project Setup** ✅

  - [x] Create `src/backend/` structure
  - [x] Set up `requirements.txt` with dependencies
  - [x] Create `config.toml` with default configuration
  - [x] Set up `.gitignore` for Python

- [x] **1.2 Core Flight Tracker** ✅

  - [x] Implement `tracker.py` with FlightRadar24 integration
  - [x] Geocoding functionality (address → coordinates)
  - [x] Flight filtering by radius
  - [x] Flight data model/schema

- [x] **1.3 FastAPI Server** ✅

  - [x] Create `main.py` with FastAPI app
  - [x] Implement GET `/api/flights` endpoint
  - [x] Implement GET `/api/config` endpoint
  - [x] Implement PUT `/api/config` endpoint
  - [x] Implement GET `/api/activities` endpoint
  - [x] Implement GET `/api/health` endpoint
  - [x] Add CORS middleware for frontend access

- [x] **1.4 Activity Logging System** ✅

  - [x] Create logging utility with categories
  - [x] In-memory activity log storage
  - [x] Log rotation/limits
  - [x] Integration with all endpoints

- [x] **1.5 Testing & Documentation** ✅
  - [x] Create README.md with setup instructions
  - [x] Manual API testing ready
  - [x] Document all endpoints

**Dependencies**: FlightRadar24-API, fastapi, uvicorn, geopy, toml, python-multipart

**Success Criteria**:

- Backend runs on `http://localhost:8000`
- Can fetch flights for a given location
- Configuration can be updated via API
- Activity logs are recorded and retrievable

---

## Phase 2: Web Frontend (User Interface)

**Priority**: HIGH - Needed for easy configuration and monitoring

### Tasks

- [x] **2.1 Project Setup** ✅

  - [x] Create `src/frontend/` structure
  - [x] Initialize Vite + React + TypeScript project
  - [x] Set up dependencies (react-router-dom, etc.)
  - [x] Configure Vite for dev server

- [x] **2.2 Core Infrastructure** ✅

  - [x] Create TypeScript types (`types.ts`)
  - [x] Implement API client (`api.ts`)
  - [x] Set up theme system (`theme.ts`) with useTheme hook
  - [x] Create main App component with routing
  - [x] Design global CSS with custom properties

- [x] **2.3 Components** ✅

  - [x] `WaveshareDisplay.tsx` - E-ink display simulator (250x122)
  - [x] `FlightBoard.tsx` - Table view of flights
  - [x] `ThemeSwitch.tsx` - Light/dark/auto theme toggle
  - [x] `Settings.tsx` - Configuration form

- [x] **2.4 Pages** ✅

  - [x] `Tracker.tsx` - Main page with display + flight board + settings
  - [x] `Activities.tsx` - Activity log viewer with filtering
  - [x] Navigation between pages

- [x] **2.5 Features** ✅

  - [x] Polling system (3-5 second intervals)
  - [x] Real-time flight updates
  - [x] Configuration updates
  - [x] Activity log streaming with auto-refresh
  - [x] Session statistics display
  - [x] Responsive design

- [x] **2.6 Testing & Documentation** ✅
  - [x] Create README.md with comprehensive documentation
  - [x] Startup script created
  - [x] Ready for manual testing

**Dependencies**: react, react-dom, react-router-dom, typescript, vite

**Success Criteria**: ✅ ALL COMPLETE

- ✅ Frontend runs on `http://localhost:5173`
- ✅ Can view live flights from backend
- ✅ Can update configuration via Settings page
- ✅ Display simulator accurately represents e-ink screen
- ✅ Theme switching works correctly (light/dark/auto)
- ✅ Activity logs visible with filtering
- ✅ Session statistics tracking

---

## Phase 3: Raspberry Pi Client (Hardware Integration) ✅

**Priority**: MEDIUM - Hardware component, can develop after backend/frontend  
**Status**: COMPLETE

### Tasks

- [x] **3.1 Project Setup** ✅

  - [x] Create `src/raspi/` structure
  - [x] Set up `requirements.txt` with dependencies
  - [x] Create `config.toml` for raspi-specific config
  - [x] Set up `__init__.py` files

- [x] **3.2 Core Components** ✅

  - [x] `tracker.py` - Flight tracking logic (API + standalone modes)
  - [x] `agent.py` - Main agent with boot sequence
  - [x] `utils.py` - Utility functions
  - [x] `log.py` - Session logging system
  - [x] `faces.py` - ASCII art faces for boot screen

- [x] **3.3 API Client** ✅

  - [x] `api_client.py` - Backend API client
  - [x] Connection error handling
  - [x] Health checks

- [x] **3.4 UI System** ✅

  - [x] `ui/__init__.py`
  - [x] `ui/display.py` - Main display controller
  - [x] `ui/view.py` - Screen rendering logic (matching e-ink layout)
  - [x] `ui/fonts.py` - Font management with fallbacks
  - [x] Boot screen renderer
  - [x] Flight screen renderer

- [x] **3.5 Hardware Drivers** ✅

  - [x] `ui/hw/__init__.py`
  - [x] `ui/hw/base.py` - Base display interface
  - [x] `ui/hw/waveshare213in_v4.py` - Waveshare 2.13" V4 driver
  - [x] Setup guides for Waveshare libraries
  - [x] Setup guides for fonts

- [x] **3.6 Testing & Documentation** ✅
  - [x] Comprehensive README.md with setup instructions
  - [x] Raspberry Pi hardware setup guide (SPI, GPIO)
  - [x] Systemd service configuration
  - [x] Troubleshooting guide
  - [x] Graceful handling when running without hardware

**Dependencies**: Pillow, RPi.GPIO (for hardware), spidev, FlightRadar24-API (if standalone), requests (if using backend)

**Success Criteria**:

- ✅ Raspi client can run in standalone mode
- ✅ Raspi client can connect to backend API
- ✅ E-ink display shows boot screen
- ✅ Flights cycle on display
- ✅ Session statistics are tracked
- ✅ Graceful fallback when hardware unavailable
- Configuration is respected

---

## Phase 4: Scripts & Automation

**Priority**: LOW - Nice to have, makes deployment easier

### Tasks

- [ ] **4.1 Startup Scripts**

  - [ ] `scripts/start-backend.sh` - Start backend server
  - [ ] `scripts/start-frontend.sh` - Start frontend dev server
  - [ ] `scripts/start-flight-tracker.sh` - Start both backend + frontend
  - [ ] `scripts/run-raspi-client.sh` - Launch Raspberry Pi client

- [ ] **4.2 Development Tools**

  - [ ] `scripts/test-api.sh` - Quick API testing script
  - [ ] `scripts/check-config.sh` - Validate configuration files

- [ ] **4.3 Deployment**
  - [ ] Production build script for frontend
  - [ ] Systemd service files for Raspberry Pi auto-start
  - [ ] Environment setup scripts

**Success Criteria**:

- Can start entire system with one command
- Scripts are well-documented
- Easy deployment to Raspberry Pi

---

## Phase 5: Documentation & Polish

**Priority**: LOW - After everything works

### Tasks

- [ ] **5.1 Documentation**

  - [ ] Update root README.md with full project info
  - [ ] API documentation (endpoints, request/response formats)
  - [ ] Frontend usage guide
  - [ ] Raspberry Pi setup guide
  - [ ] Troubleshooting guide
  - [ ] Architecture diagrams

- [ ] **5.2 Code Quality**

  - [ ] Add type hints to all Python code
  - [ ] Add docstrings to all functions/classes
  - [ ] Consistent code formatting
  - [ ] Error handling review

- [ ] **5.3 Testing**

  - [ ] Unit tests for backend
  - [ ] Integration tests
  - [ ] End-to-end testing

- [ ] **5.4 Enhancements**
  - [ ] Better error messages
  - [ ] Loading states in frontend
  - [ ] Graceful degradation if API is down
  - [ ] Performance optimization

**Success Criteria**:

- Complete documentation
- Clean, maintainable code
- Tested and reliable system

---

## Technical Specifications

### Backend API Endpoints

```
GET  /api/flights         → List current flights
GET  /api/config          → Get configuration
PUT  /api/config          → Update configuration
GET  /api/activities      → Get activity logs
GET  /api/health          → Health check
```

### Configuration Schema

```toml
[main]
address = "Your Location"
search_radius_meters = 3000
max_flights = 20
max_elapsed_time = 1800

[ui]
boot_screen_duration = 10
scan_update_interval = 2
flight_display_duration = 5

[ui.display]
enabled = true
type = "waveshare213in_v4"
rotation = 180
color = "black"

[api]
backend_url = "http://localhost:8000"
```

### Flight Data Model

```typescript
interface Flight {
  id: string;
  callsign: string;
  registration: string;
  aircraft: string;
  airline: string;
  origin: string;
  destination: string;
  altitude: number;
  speed: number;
  heading: number;
  latitude: number;
  longitude: number;
  distance: number;
  timestamp: string;
}
```

---

## Development Workflow

### Recommended Order

1. **Start with Backend** (Phase 1)

   - Get flight tracking working first
   - Test with curl or Postman
   - Verify FlightRadar24 integration

2. **Build Frontend** (Phase 2)

   - Develop UI while backend is stable
   - Test integration between frontend and backend
   - Ensure all features work via web UI

3. **Implement Raspberry Pi Client** (Phase 3)

   - Hardware integration last
   - Test with mock display first
   - Deploy to actual Raspberry Pi when ready

4. **Add Scripts** (Phase 4)

   - Automate startup and deployment
   - Make life easier

5. **Polish** (Phase 5)
   - Documentation and testing
   - Make it production-ready

### Testing Strategy

- **Backend**: Manual API testing with curl/Postman, then automated tests
- **Frontend**: Browser testing, multiple themes, responsive design
- **Raspberry Pi**: Mock display first, then real hardware testing
- **Integration**: Full end-to-end testing with all components running

---

## Dependencies Summary

### Backend (Python)

```
fastapi
uvicorn[standard]
FlightRadar24-API
geopy
toml
python-multipart
pydantic
```

### Frontend (Node.js)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

### Raspberry Pi (Python)

```
Pillow
FlightRadar24-API (if standalone)
requests (if using backend)
RPi.GPIO
spidev
toml
```

---

## Known Challenges & Solutions

### Challenge 1: FlightRadar24 API Rate Limiting

**Solution**: Implement intelligent caching, reasonable polling intervals, consider upgrading to paid tier

### Challenge 2: E-ink Display Refresh Speed

**Solution**: Rotate flights slowly (5 seconds each), optimize rendering

### Challenge 3: Network Reliability on Raspberry Pi

**Solution**: Retry logic, fallback to standalone mode, error handling

### Challenge 4: Configuration Synchronization

**Solution**: Backend is source of truth, all clients poll for config updates

### Challenge 5: Testing Without Hardware

**Solution**: Mock display implementation for development

---

## Success Metrics

- [ ] Backend responds to all API calls correctly
- [ ] Frontend displays live flight data
- [ ] Configuration can be changed via web UI
- [ ] Raspberry Pi displays flights on e-ink screen
- [ ] System runs for 24+ hours without crashes
- [ ] Documentation is complete and accurate
- [ ] Code is clean and maintainable

---

## Next Steps

**Immediate Action**: Start with Phase 1.1 - Backend Project Setup

1. Create backend directory structure
2. Set up requirements.txt
3. Create config.toml
4. Begin implementing tracker.py

**After Phase 1**: Move to frontend development while testing backend in parallel

---

## Notes

- Archive folder (`_archive/`) contains reference implementation - use as guide but don't modify
- All new development happens in root `src/` directory
- Context document at `_context/llm.txt` contains full system understanding
- Follow polling-based architecture (no WebSockets)
- Keep it simple and reliable

---

## Questions to Address

- [ ] Which FlightRadar24 API library/version to use?
- [ ] Specific Raspberry Pi model and OS version?
- [ ] Deployment environment (systemd service or manual start)?
- [ ] Logging destination (file, stdout, or both)?
- [ ] Error notification method (logs only or email/alerts)?

---

**Remember**: Build incrementally, test frequently, commit often. Each phase should result in a working component before moving to the next phase.
