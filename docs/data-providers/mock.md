# Deterministic mock provider

Status: implemented in the new API core.

## Purpose

The mock provider is the default development and automated-test source. It
provides seeded, reproducible aircraft movement without network access,
credentials, payment, or physical hardware.

## Capabilities

It declares live position, altitude, ground speed, heading, registration,
aircraft type, airline, route, and airport capabilities. Its normal scenario
includes:

- several aircraft on different bearings, tracks, distances, and altitudes;
- an aircraft that enters, crosses, and leaves a north-facing viewing sector;
- complete enrichment for normal records;
- deliberately partial live state and enrichment for one record.

Explicit scenarios cover normal movement, empty sky, timeout, and rate limit.
The simulation advances one 30-second frame for every live-state request and
can be reset.

## Authentication and licensing

No authentication is required. All records are synthetic project data, so
there are no external redisplay or retention constraints.

## Caching and fallback

Mock live and enrichment data may be cached without restriction. It is the
safe local/CI fallback and must never silently represent itself as real flight
data in a production environment.

