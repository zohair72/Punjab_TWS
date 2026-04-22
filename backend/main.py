from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.config import settings
    from backend.routes.health import router as health_router
    from backend.routes.methodology import router as methodology_router
    from backend.routes.summary import router as summary_router
    from backend.routes.timeline import router as timeline_router
    from backend.services.data_loader import data_loader
except ImportError:  # pragma: no cover - supports Render/service-root execution inside backend/
    from config import settings
    from routes.health import router as health_router
    from routes.methodology import router as methodology_router
    from routes.summary import router as summary_router
    from routes.timeline import router as timeline_router
    from services.data_loader import data_loader


# Windows Proactor pipes can emit noisy ConnectionResetError traces on client
# disconnects in local development. The selector policy is usually quieter.
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        data_loader.refresh_cache()
    except Exception:
        # The API should still boot even before the first pipeline sync has run.
        pass
    yield


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_origin_regex=settings.frontend_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(timeline_router, prefix="/api/timeline", tags=["timeline"])
app.include_router(summary_router, prefix="/api/summary", tags=["summary"])
app.include_router(methodology_router, prefix="/api/methodology", tags=["methodology"])


@app.get("/")
def root() -> dict[str, object]:
    return {
        "message": "Punjab Groundwater Stress Dashboard API",
        "description": (
            "Serves stored Punjab-scale GRACE TWS anomaly and matching GLDAS context "
            "from processed files."
        ),
        "route_groups": ["/health", "/api/timeline", "/api/summary", "/api/methodology"],
    }
