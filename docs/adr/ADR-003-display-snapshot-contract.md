# ADR-003: Semantic display snapshot contract

Status: accepted  
Date: 2026-08-08

## Context

The current Pi requests flight lists and configuration separately, rotates raw
flight objects, and owns decisions that should be consistent across devices.
Future hardware may not run Linux or Python and may use different screen sizes.

## Decision

A device receives one small semantic `DisplaySnapshot` containing generation
time, explicit status, backend-controlled refresh policy, optional primary
aircraft content, and a secondary count. The backend owns viewing-zone matching,
ranking, and enrichment. Device renderers own screen-specific layout and avoid
refreshing unchanged content.

## Consequences

The Pi and web simulator can share fixtures and state semantics. Devices make
fewer requests and do less work. Adding fields requires deliberate contract
evolution, while changing providers or ranking does not require firmware
changes.

