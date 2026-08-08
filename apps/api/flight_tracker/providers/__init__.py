"""Replaceable flight-data provider adapters."""

from .base import FlightDataProvider, GeographicArea, ProviderCapability
from .mock import MockFlightDataProvider, MockScenario

__all__ = [
    "FlightDataProvider",
    "GeographicArea",
    "MockFlightDataProvider",
    "MockScenario",
    "ProviderCapability",
]
