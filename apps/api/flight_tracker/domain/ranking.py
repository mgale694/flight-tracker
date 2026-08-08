"""Explainable relevance ranking for visible aircraft."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from .models import ViewingZone, VisibleAircraft

ANGULAR_WEIGHT = 0.70
DISTANCE_WEIGHT = 0.20
COMPLETENESS_WEIGHT = 0.10


def _data_completeness(match: VisibleAircraft) -> float:
    aircraft = match.aircraft
    values = (
        aircraft.callsign,
        aircraft.registration,
        aircraft.altitude_ft,
        aircraft.ground_speed_knots,
        aircraft.track_degrees,
    )
    populated = sum(value is not None and value != "" for value in values)
    return populated / len(values)


def relevance_score(match: VisibleAircraft, zone: ViewingZone) -> float:
    """Score a visible aircraft using documented, bounded components."""

    if not match.inside_view:
        return 0.0

    half_view = zone.field_of_view_degrees / 2.0
    angular_score = max(0.0, 1.0 - match.relative_bearing_degrees / half_view)

    distance_span = zone.max_distance_km - zone.min_distance_km
    if distance_span <= 0.0:
        distance_score = 1.0
    else:
        normalised_distance = (match.distance_km - zone.min_distance_km) / distance_span
        distance_score = max(0.0, min(1.0, 1.0 - normalised_distance))

    score = (
        ANGULAR_WEIGHT * angular_score
        + DISTANCE_WEIGHT * distance_score
        + COMPLETENESS_WEIGHT * _data_completeness(match)
    )
    return round(score, 6)


def rank_visible_aircraft(
    matches: Iterable[VisibleAircraft], zone: ViewingZone
) -> list[VisibleAircraft]:
    """Return visible aircraft ordered by relevance with deterministic ties."""

    scored = [
        replace(match, relevance_score=relevance_score(match, zone))
        for match in matches
        if match.inside_view
    ]
    return sorted(
        scored,
        key=lambda match: (
            -match.relevance_score,
            match.distance_km,
            match.aircraft.provider_aircraft_id,
        ),
    )
