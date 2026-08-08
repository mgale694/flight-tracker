# Flight Tracker API core

This directory is the incremental home of the product backend. The first slice
contains framework-independent domain, provider, visibility, ranking, and
snapshot logic. The existing FastAPI app under `src/backend` remains the
runnable compatibility application while versioned routes and persistence are
built around this core.

Run the dependency-free core tests with:

```bash
cd apps/api
python3 -m unittest discover -s tests -v
```

The deterministic mock provider is the default development boundary; no live
flight API or hardware is needed by these tests.

