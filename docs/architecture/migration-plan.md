# Incremental Migration Plan

## Approach

Build the product architecture beside the prototype and migrate one contract at
a time. Do not move directories simply to match a diagram, and do not delete a
working route or hardware path before its replacement has automated coverage
and a migrated caller.

Each phase below has an exit gate. A phase can overlap preparatory work from the
next one, but its gate must be met before legacy functionality is removed.

## Phase 0 — Audit

Status: complete as of 2026-08-08.

- Record entry points, routes, providers, geocoding, configuration, display
  code, duplicated models, tests, and removal candidates.
- Capture the baseline build/lint/test state.
- Agree on modular-monolith target boundaries and a staged directory move.

Exit gate: `current-state.md`, `target-state.md`, and this plan exist and match
the repository.

## Phase 1 — Isolated core foundation

Status: in progress.

- Introduce `apps/api/flight_tracker` as an importable, framework-independent
  core package.
- Add explicit domain models and validation for users, devices, viewing zones,
  aircraft, enrichment, visible matches, and display snapshots.
- Add stable domain/application errors.
- Keep the existing `src/backend` application runnable and unchanged.
- Establish test discovery that does not require live APIs.

Exit gate: new core tests pass locally and legacy Python sources still compile.

## Phase 2 — Provider boundary and deterministic development

- Define asynchronous `FlightDataProvider` and explicit provider capabilities.
- Add a seeded moving mock provider with normal, empty, timeout, rate-limit,
  complete-enrichment, and partial-enrichment behaviours.
- Wrap current FlightRadar parsing in an adapter using recorded/legally safe
  fixtures.
- Add one provider contract suite and run it against every adapter.
- Add typed settings with `FLIGHT_PROVIDER=mock` as the local default.
- Document provider authentication, licensing questions, caching constraints,
  failure behaviour, and cost assumptions under `docs/data-providers/`.

Exit gate: application services import only the provider protocol, CI uses the
mock provider, and no provider payload escapes an adapter.

## Phase 3 — Viewing zone and snapshot application service

- Implement haversine distance, initial bearing, 0/360-safe angular difference,
  distance/altitude filtering, and explainable ranking.
- Generate all required `DisplaySnapshot` states and degrade cleanly when
  enrichment is absent.
- Define regional live-state and enrichment cache interfaces; add an in-memory
  implementation first and Redis where shared caching becomes useful.
- Ensure snapshot content is semantic and screen-size independent.

Exit gate: comprehensive geometry/ranking/snapshot tests pass with deterministic
mock aircraft entering and leaving a sector.

## Phase 4 — PostgreSQL product state

- Add SQLAlchemy 2 models and repositories for users, devices, credentials,
  viewing zones, and detections.
- Add Alembic configuration and an initial migration.
- Add repository integration tests against PostgreSQL.
- Implement device secret hashing, revocation, rotation, last-seen, and version
  reporting.
- Implement short-lived pairing sessions and ownership rules.
- Convert useful aircraft entry/primary/exit transitions into detection events;
  do not persist every raw poll.

Exit gate: product configuration is database-backed, migration upgrade/downgrade
is tested, and precise location is protected by ownership checks.

## Phase 5 — Versioned API

- Create a professional FastAPI application under `apps/api` with lifespan
  wiring, typed settings, structured logging, and narrow environment-driven
  CORS.
- Add `/health/live`, `/health/ready`, and grouped system/provider status.
- Add `/api/v1` device, pairing, viewing-zone, snapshot, and history routes.
- Authenticate web users and devices separately.
- Translate known domain errors into a stable API error model.
- Keep legacy `/api/*` routes temporarily, delegating to new services where
  possible and marking them deprecated in OpenAPI.

Exit gate: device snapshot and web setup integration tests cover ownership,
pairing, no-aircraft, multiple-aircraft, provider failure, partial data, and
cache reuse.

## Phase 6 — Next.js web migration

- Create `apps/web` with App Router, Tailwind, Zod, canonical tokens, and a
  small accessible primitive layer.
- Generate or validate shared TypeScript contracts from the versioned API.
- Build mobile-first routes for setup, location, window direction, sector
  preview, device dashboard/settings/history, and display simulator.
- Reuse the existing preview/layout ideas without recreating the dashboard as
  the primary product.
- Fix the current Vite lint baseline as code is migrated; keep the Vite app
  available until the new critical flows pass.

Exit gate: key setup and display-preview flows pass production build,
typecheck, lint, and browser tests on mobile and desktop viewports.

## Phase 7 — Pi snapshot client

- Split client auth/API, semantic rendering, panel layouts, hardware adapters,
  simulator, and settings under `apps/device-pi`.
- Request only the authenticated snapshot endpoint.
- Render setup, scanning, no-aircraft, one/multiple-aircraft, degraded, and
  offline states.
- Honour backend refresh policy (normally 15–60 seconds), compare semantic
  snapshots, and skip unchanged physical refreshes.
- Retain useful stale content during transient connectivity loss.
- Preserve Waveshare V4 support and test rendering without GPIO.

Exit gate: the Pi normal path has no FlightRadar/geopy imports and the same
snapshot fixtures drive both Pi and web simulator tests.

## Phase 8 — Development and production quality

- Add Docker Compose for API, web, PostgreSQL, Redis (when enabled), and mock
  provider mode.
- Add `.env.example`, Make targets, CI checks, migration validation, secret and
  dependency checks, and concise runbooks.
- Add request IDs, structured privacy-safe logs, bounded provider retry, cache
  metrics, snapshot latency, and device activity monitoring.
- Review API payload size, polling defaults, location handling, provider
  licensing, and CORS/session configuration.
- Replace repeated root/component documentation with links to canonical docs.

Exit gate: a new developer can run the complete product without hardware or
paid credentials, all required CI checks pass, and the reference Pi remains
supported.

## Legacy removal order

1. Remove the Pi standalone provider mode only after snapshot rendering is the
   tested default.
2. Remove direct FlightRadar use from `src/backend` only after the adapter and
   compatibility routes are tested.
3. Remove TOML writes only after viewing-zone persistence and migration tooling
   are operational.
4. Remove Vite only after the Next.js setup/dashboard/simulator flows pass.
5. Remove generic activity endpoints only after customer detections and
   engineering observability are separately available.
6. Remove legacy launch scripts only after replacement local and Pi commands
   are documented and exercised.

## Immediate redevelopment slice

The first code slice implements, without changing current runtime paths:

- core domain models and stable statuses;
- provider protocol, capabilities, errors, and deterministic mock scenarios;
- visible-sky geometry and explainable ranking;
- snapshot generation with graceful degradation;
- unit and contract-style tests using only deterministic local data.

This slice creates the seam required for later FastAPI, persistence, web, and
device migration while keeping the existing prototype usable.
