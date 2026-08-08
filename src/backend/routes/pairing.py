"""Prototype device-pairing routes used during the persistence migration."""

from fastapi import APIRouter, HTTPException, status

from models import PairDeviceRequest, PairingStatus
from models.enums import ActivityCategory
from services import ActivityLoggerService, ConfigService

router = APIRouter(prefix="/api/v1/devices", tags=["device setup"])


def setup_pairing_routes(
    config_service: ConfigService,
    activity_service: ActivityLoggerService,
):
    """Register simulated provisioning routes for the single prototype device."""

    def current_pairing_status(device_id: str) -> PairingStatus:
        device = config_service.get_device_config()
        if device.get("public_id") != device_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found",
            )
        return PairingStatus(
            device_id=device_id,
            paired=bool(device.get("paired", False)),
            setup_url=str(device.get("setup_url", "")),
        )

    @router.get(
        "/{device_id}/pairing-status",
        response_model=PairingStatus,
        summary="Get prototype device pairing status",
    )
    async def get_pairing_status(device_id: str) -> PairingStatus:
        return current_pairing_status(device_id)

    @router.post(
        "/{device_id}/pair",
        response_model=PairingStatus,
        summary="Pair the provisioned prototype device",
    )
    async def pair_device(device_id: str, request: PairDeviceRequest) -> PairingStatus:
        try:
            config_service.pair_device(device_id, request.pairing_code)
        except LookupError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found",
            ) from error
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Pairing code is invalid",
            ) from error

        activity_service.log(
            ActivityCategory.CONFIG,
            "Prototype device paired",
            {"device_id": device_id},
        )
        return current_pairing_status(device_id)

    return router

