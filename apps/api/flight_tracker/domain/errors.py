"""Stable domain and application errors."""


class FlightTrackerError(Exception):
    """Base class for expected product errors."""


class DomainValidationError(FlightTrackerError, ValueError):
    """Raised when a domain value violates an invariant."""


class ViewingZoneNotConfigured(FlightTrackerError):
    """Raised when a device has no usable viewing zone."""


class ProviderError(FlightTrackerError):
    """Base class for errors translated at the provider boundary."""


class ProviderUnavailable(ProviderError):
    """The provider cannot currently serve a request."""


class ProviderTimeout(ProviderUnavailable):
    """The provider did not respond within its bounded timeout."""


class ProviderResponseInvalid(ProviderError):
    """The provider returned a payload that could not be normalised safely."""


class ProviderRateLimited(ProviderUnavailable):
    """The provider rejected a request because its rate limit was reached."""

    def __init__(self, message: str, *, retry_after_seconds: int | None = None) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds
