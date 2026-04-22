from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

try:
    from ..services.data_loader import data_loader
except ImportError:  # pragma: no cover - supports running inside backend/ directly.
    from services.data_loader import data_loader

router = APIRouter()


class MethodologyResponse(BaseModel):
    project_scope: str
    primary_signal: str
    gldas_role: str
    limitations: list[str]
    not_groundwater_measurement: str
    scale_note: str
    datasets_used: list[str]


@router.get("", response_model=MethodologyResponse)
def get_methodology() -> MethodologyResponse:
    metadata = data_loader.get_metadata()
    datasets_used = metadata.get(
        "datasets_used",
        [
            "NASA/GRACE/MASS_GRIDS_V04/MASCON",
            "NASA/GLDAS/V021/NOAH/G025/T3H",
        ],
    )

    return MethodologyResponse(
        project_scope=(
            "Punjab-scale terrestrial water storage anomaly dashboard for regional monitoring."
        ),
        primary_signal=(
            "GRACE/GRACE-FO provides Punjab-wide terrestrial water storage anomaly (TWSA), "
            "which reflects integrated water storage changes rather than direct groundwater measurements."
        ),
        gldas_role=(
            "GLDAS variables are stored as same-month contextual support data to help interpret "
            "Punjab-scale hydrologic conditions alongside GRACE."
        ),
        limitations=[
            "This API serves regional Punjab-scale outputs only.",
            "District boundaries are not analytical units.",
            "Outputs support interpretation and monitoring, not local aquifer quantification.",
            "The backend serves stored processed files and does not query Earth Engine live.",
        ],
        not_groundwater_measurement=(
            "TWS anomaly is not a direct groundwater measurement; it is a broader terrestrial water storage signal."
        ),
        scale_note=(
            "All summary values are aggregated to Punjab province scale."
        ),
        datasets_used=list(datasets_used),
    )
