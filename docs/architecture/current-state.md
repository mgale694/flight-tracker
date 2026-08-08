# Current State Audit

Date: 2026-08-08  
Repository: `flight-tracker`  
Audit baseline: `main` at `1c3174e`

## Summary

The repository is a useful, runnable prototype with three applications under
`src/`: a FastAPI backend, a Vite/React web dashboard, and a Raspberry Pi
client for the Waveshare 2.13-inch V4 e-paper panel. The hardware abstraction
and display renderer are worth preserving. The largest product gap is that the
system selects aircraft by radius, not by the part of the sky visible through a
window.

The prototype is small enough to migrate incrementally. The redevelopment
should build tested product boundaries beside the current paths, move callers
one at a time, and remove legacy paths only after their replacements work.

## Application entry points

| Application | Entry point | Current start path |
| --- | --- | --- |
| Backend | `src/backend/main.py` | `python main.py` from `src/backend` |
| Web | `src/frontend/src/main.tsx` | Vite via `npm run dev` |
| Pi device | `src/raspi/agent.py` | `python3 agent.py` from `src/raspi` |
| Combined desktop | `scripts/start-flight-tracker.sh` | Starts backend and Vite |
| Combined Pi | `scripts/start-raspi-all.sh` | Builds/starts all three applications |

The Python imports rely on the current working directory rather than an
installed package. This makes the entry points sensitive to where they are
launched.

## Backend

### Routes

All current product routes are unversioned below `/api`:

| Route | Responsibility |
| --- | --- |
| `GET /` | API metadata |
| `GET /api/health` | Combined liveness-style health response |
| `GET /api/flights` | Geocode configured address, query FlightRadar24, enrich and return nearby aircraft |
| `GET /api/flight/{flight_id}` | Return provider-specific flight details |
| `GET /api/config` | Return TOML configuration |
| `PUT /api/config` | Mutate TOML configuration |
| `GET /api/activities` | Return in-memory diagnostic/customer activity entries |
| `DELETE /api/activities` | Clear in-memory activity entries |
| `POST /api/system/clear-display` | Send a Unix signal to a local Pi process |
| `POST /api/system/shutdown` | Terminate processes matching a local pattern |

Routes use closure-based dependency injection. They are generally short, but
they translate broad exceptions into arbitrary error strings and expose a
provider-shaped flight model.

### Flight data and geocoding

`src/backend/services/flight_service.py` owns all of the following:

- construction and direct use of `FlightRadar24API`;
- Nominatim geocoding through `geopy`;
- one-entry address/coordinate caching;
- approximate bounding-box construction;
- circular distance filtering;
- an enrichment request for every in-range aircraft;
- provider-object parsing and legacy array parsing;
- airline inference and provider detail lookup.

This module is synchronous and is called from `async` FastAPI handlers, so
network I/O can block the event loop. Provider failures are frequently reduced
to an empty list, which makes an outage indistinguishable from an empty sky.
Provider payload details escape through `GET /api/flight/{flight_id}`.

The longitude bounding-box approximation divides by `abs(latitude / 90)`
rather than the cosine of latitude. It is not a safe geospatial primitive and
should not be reused in the new domain.

### Configuration and storage

`src/backend/config.toml` is both bootstrap configuration and mutable product
state. `ConfigService` reads and rewrites it directly. It stores one global
address/radius configuration and cannot represent users, device ownership, or
multiple viewing zones. There is no database, migration tool, repository
boundary, Redis integration, or durable detection history.

Current mapping candidates are:

| Prototype field | Product meaning |
| --- | --- |
| `address` | Geocoding input/address metadata; resolved coordinates belong to a `ViewingZone` |
| `search_radius_meters` | `ViewingZone.max_distance_km` |
| `max_flights` | Deprecated in favour of ranking/snapshot policy |
| `max_elapsed_time` | Provider freshness/cache policy |
| `display_hold_time` | Display stale-content/refresh policy |
| `display_fields` | Device layout preference, not flight-domain state |

### Activity and observability

`ActivityLoggerService` stores a maximum of 500 dictionary entries in a
process-local deque. Entries mix customer events, provider diagnostics, health
checks, and configuration events. They disappear on restart and do not support
detection lifecycle semantics. Logging is mostly unstructured `print` and
standard logging output. There are no request IDs, provider metrics, readiness
checks, or privacy controls; the current radar log includes the configured
address.

### Security and API quality

- CORS uses `allow_origins=["*"]` together with credentials.
- There is no account, ownership, pairing, or device authentication.
- Device/provider secrets have no separate model.
- Process-control routes are unauthenticated and coupled to a Linux host.
- Exact address data can appear in logs.
- Health, product, activity, and machine-control routes share one flat API.
- The FastAPI application still uses deprecated event registration rather than
  a lifespan context.

## Web application

The web client is React 19, TypeScript, React Router, and Vite. It has tracker,
settings, and activity pages. Reusable prototype concepts include:

- the 250 by 122 e-paper preview;
- configurable display fields;
- responsive CSS and shared design tokens;
- a central API client;
- session flight history and status displays.

The product experience is currently a live dashboard rather than setup and
window-oriented onboarding. API types are handwritten in `src/frontend/src/types.ts`
and mirror the legacy backend shape. Runtime response validation is absent.
The global flight context polls `/api/flights` every five seconds and keeps
session-only history. A display hold calculation is performed during render.

The frontend contains a central `fetch` wrapper, but it returns unvalidated
JSON and includes an `any` detail response. There is no Next.js App Router,
Tailwind, Zod, shared contract package, account/session boundary, or device
feature boundary yet.

## Raspberry Pi and display implementation

The Pi client has a useful separation between display control, view rendering,
font management, and a Waveshare-specific driver:

- `src/raspi/ui/hw/base.py` defines the current display implementation shape;
- `src/raspi/ui/hw/waveshare213in_v4.py` isolates panel/vendor interaction;
- `src/raspi/ui/view.py` renders monochrome PIL images;
- `src/raspi/ui/display.py` coordinates the implementation and view.

The layout is hard-coded around 250 by 122 pixels in the base implementation,
but the semantic renderer and hardware adapter are separable and should be
migrated rather than discarded.

`src/raspi/tracker.py` supports a backend mode and a direct FlightRadar24
standalone mode. Backend mode makes separate flights/config/health calls and
converts dictionaries into attribute bags. Standalone mode duplicates
provider, geocoding, bounds, and distance logic. The main agent fetches every
10 seconds, rotates every 5 seconds by default, and does not render explicit
no-aircraft, provider-degraded, offline, or pairing states. Shutdown clears the
e-paper screen rather than retaining useful stale content.

## Duplicated or tightly coupled models

- Flight data is represented as a Pydantic `FlightData`, a handwritten
  TypeScript `Flight`, a dynamic Pi `FlightData` attribute bag, FlightRadar
  objects, and loose dictionaries.
- Configuration is independently understood by backend Pydantic models,
  `ConfigService`, TypeScript interfaces/forms, Pi TOML, and renderer code.
- Display semantics are inferred independently by the web simulator and Pi
  renderer rather than supplied by a shared `DisplaySnapshot` contract.
- FlightRadar response fields and fallback strings such as `"N/A"` are mixed
  into business and presentation logic.

## Tests and baseline health

There is no automated unit, integration, contract, or frontend test suite.
`src/raspi/test_display.py` is a manual hardware diagnostic script.

Baseline commands run during this audit:

| Check | Result |
| --- | --- |
| `python3 -m compileall -q src/backend src/raspi` | Pass |
| `python3 -m pytest -q` | Not runnable; pytest is not installed and no suite exists |
| `npm run build` in `src/frontend` | Pass |
| `npm run lint` in `src/frontend` | Fail: 5 errors and 2 warnings |

The lint baseline comprises two explicit `any` uses, a Fast Refresh export
warning, synchronous state work initiated from an effect, missing effect
dependencies, and an impure `Date.now()` render call.

## Dead or obsolete code candidates

These items require replacement tests before removal:

- `_parse_flight_data` in `FlightTrackerService`, marked as legacy;
- the Pi direct-provider mode and its FlightRadar/geopy dependencies;
- the unauthenticated `/api/system/*` process-control routes;
- generic in-memory activity history as a customer-facing feature;
- root `requirements.txt`, which describes an older Streamlit/PyQt application
  and contains a malformed final dependency line;
- Vite starter assets;
- repeated and stale setup material across root/backend/frontend/Pi READMEs;
- archive directories ignored by the repository's `_*/` rule.

## Preserve during migration

- existing FastAPI endpoints until new consumers have moved;
- FlightRadar parsing knowledge, extracted behind fixtures and an adapter;
- the PIL e-paper rendering techniques and Waveshare driver isolation;
- the web display preview and responsive layout concepts;
- working launch scripts until replacement development commands exist.
