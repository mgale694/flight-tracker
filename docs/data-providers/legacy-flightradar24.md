# Legacy FlightRadar24 integration

Status: prototype-only, adapter migration pending.

## Current API and authentication

The prototype uses the third-party Python package `FlightRadarAPI==1.3.23` and
constructs `FlightRadar24API()` without credentials. It calls `get_flights`
with geographic bounds and requests `get_flight_details` for each in-range
aircraft.

This implementation is not yet behind the product `FlightDataProvider`
boundary. Backend and optional Pi standalone paths both import it directly.

## Commercial and legal status

Commercial-use, derivative-display, redisplay, caching, retention, and service
availability rights are not established anywhere in the repository. No
production or commercial right should be inferred from the prototype working.
These questions require written provider terms or a commercial agreement
before production use.

## Rate limits and cost model

No authoritative limit or cost model is documented in the repository. The
current implementation may make one detail request per in-range aircraft on
each poll, which is unsuitable as a commercial unit-economics assumption.

## Required adapter migration

1. Capture representative, legally safe fixtures.
2. Map live payloads only to `AircraftState`.
3. Map detail payloads only to `FlightInformation`.
4. Add bounded timeouts/retries and explicit rate-limit/error translation.
5. Declare only verified capabilities.
6. Apply cache policies only after licensing/retention review.
7. Remove direct imports from routes and the normal Pi path.

Until that work is complete, the deterministic mock is the only supported new
core provider and this integration remains a compatibility dependency.

