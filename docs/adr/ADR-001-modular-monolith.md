# ADR-001: Modular monolith

Status: accepted  
Date: 2026-08-08

## Context

The prototype is one small backend with web and Pi clients. Productisation adds
identity, devices, viewing zones, provider adapters, snapshots, persistence,
and observability, but it does not yet have a scaling need that justifies
distributed services.

## Decision

Build one FastAPI deployable with explicit domain, provider, service,
repository, schema, settings, and observability modules. Keep the web and device
as separate clients. Introduce boundaries through Python interfaces and package
ownership rather than network calls.

## Consequences

Local development and transactions remain simple. Provider or ingestion
modules can be separated later if measured load or cost requires it. Module
boundaries need tests and import discipline because deployment boundaries will
not enforce them.

