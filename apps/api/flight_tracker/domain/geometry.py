"""Deterministic great-circle and visible-sky geometry."""

from __future__ import annotations

from collections.abc import Iterable
from math import asin, atan2, cos, degrees, isclose, radians, sin, sqrt

from .models import AircraftState, ViewingZone, VisibleAircraft

EARTH_RADIUS_KM = 6_371.0088
BOUNDARY_EPSILON = 1e-9


def great_circle_distance_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Calculate the haversine distance between two WGS84 coordinates."""

    latitude_a_rad = radians(latitude_a)
    latitude_b_rad = radians(latitude_b)
    latitude_delta = radians(latitude_b - latitude_a)
    longitude_delta = radians(longitude_b - longitude_a)

    haversine = (
        sin(latitude_delta / 2.0) ** 2
        + cos(latitude_a_rad) * cos(latitude_b_rad) * sin(longitude_delta / 2.0) ** 2
    )
    arc = 2.0 * atan2(sqrt(haversine), sqrt(max(0.0, 1.0 - haversine)))
    return EARTH_RADIUS_KM * arc


def initial_bearing_degrees(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Calculate the initial bearing from coordinate A to B in [0, 360)."""

    latitude_a_rad = radians(latitude_a)
    latitude_b_rad = radians(latitude_b)
    longitude_delta = radians(longitude_b - longitude_a)

    y = sin(longitude_delta) * cos(latitude_b_rad)
    x = cos(latitude_a_rad) * sin(latitude_b_rad) - sin(latitude_a_rad) * cos(latitude_b_rad) * cos(
        longitude_delta
    )
    bearing = (degrees(atan2(y, x)) + 360.0) % 360.0
    # Floating-point noise can represent due north as 359.99999999999. Keep
    # the public invariant canonical so exact-north comparisons remain useful.
    return 0.0 if isclose(bearing, 360.0, abs_tol=1e-10) else bearing


def angular_difference_degrees(first: float, second: float) -> float:
    """Return the smallest unsigned angular difference in [0, 180]."""

    return abs((first - second + 180.0) % 360.0 - 180.0)


def destination_point(
    latitude: float,
    longitude: float,
    bearing_degrees: float,
    distance_km: float,
) -> tuple[float, float]:
    """Return a point a great-circle distance and bearing from an origin."""

    angular_distance = distance_km / EARTH_RADIUS_KM
    bearing_rad = radians(bearing_degrees)
    latitude_rad = radians(latitude)
    longitude_rad = radians(longitude)

    destination_latitude = asin(
        sin(latitude_rad) * cos(angular_distance)
        + cos(latitude_rad) * sin(angular_distance) * cos(bearing_rad)
    )
    destination_longitude = longitude_rad + atan2(
        sin(bearing_rad) * sin(angular_distance) * cos(latitude_rad),
        cos(angular_distance) - sin(latitude_rad) * sin(destination_latitude),
    )

    normalised_longitude = (degrees(destination_longitude) + 540.0) % 360.0 - 180.0
    return degrees(destination_latitude), normalised_longitude


def evaluate_aircraft(aircraft: AircraftState, zone: ViewingZone) -> VisibleAircraft:
    """Evaluate one aircraft against all viewing-zone constraints.

    Missing altitude is accepted only when the viewing zone has no altitude
    constraint. When an altitude boundary exists, the aircraft cannot be shown
    as inside the view unless its altitude is known.
    """

    distance_km = great_circle_distance_km(
        zone.latitude,
        zone.longitude,
        aircraft.latitude,
        aircraft.longitude,
    )
    bearing_degrees = initial_bearing_degrees(
        zone.latitude,
        zone.longitude,
        aircraft.latitude,
        aircraft.longitude,
    )
    relative_bearing = angular_difference_degrees(zone.bearing_degrees, bearing_degrees)

    within_angle = relative_bearing <= zone.field_of_view_degrees / 2.0 + BOUNDARY_EPSILON
    within_distance = (
        zone.min_distance_km - BOUNDARY_EPSILON
        <= distance_km
        <= zone.max_distance_km + BOUNDARY_EPSILON
    )

    altitude_is_required = zone.min_altitude_ft is not None or zone.max_altitude_ft is not None
    if aircraft.altitude_ft is None:
        within_altitude = not altitude_is_required
    else:
        above_minimum = zone.min_altitude_ft is None or aircraft.altitude_ft >= zone.min_altitude_ft
        below_maximum = zone.max_altitude_ft is None or aircraft.altitude_ft <= zone.max_altitude_ft
        within_altitude = above_minimum and below_maximum

    return VisibleAircraft(
        aircraft=aircraft,
        flight_information=None,
        distance_km=distance_km,
        bearing_degrees=bearing_degrees,
        relative_bearing_degrees=relative_bearing,
        inside_view=zone.enabled and within_angle and within_distance and within_altitude,
    )


def visible_aircraft(
    aircraft_states: Iterable[AircraftState], zone: ViewingZone
) -> list[VisibleAircraft]:
    """Return only aircraft that satisfy every viewing-zone constraint."""

    matches = (evaluate_aircraft(aircraft, zone) for aircraft in aircraft_states)
    return [match for match in matches if match.inside_view]
