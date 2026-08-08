# ADR-002: Flight-provider abstraction

Status: accepted  
Date: 2026-08-08

## Context

The prototype directly imports FlightRadar24 in backend and Pi code, mixes
provider parsing with geocoding/filtering, and treats failures as empty sky.
Commercial licensing, rate limits, capabilities, and cost may require a
different or composite data source.

## Decision

Application services depend on the asynchronous `FlightDataProvider` protocol
and normalised `AircraftState`/`FlightInformation` models. Adapters expose an
explicit capability set and translate timeout, rate-limit, unavailable, and
invalid-response failures. A seeded moving mock is the default development and
test provider.

## Consequences

Provider payloads cannot become API or hardware contracts. Live state and
enrichment can be cached independently. Each real adapter must satisfy common
behavioural tests and document its licensing/cache assumptions. The legacy
FlightRadar implementation remains until it is fixture-tested behind this
boundary.

