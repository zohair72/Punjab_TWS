from __future__ import annotations

import asyncio
import os
import sys

import uvicorn


def main() -> int:
    # On Windows, set the selector policy before Uvicorn creates the event loop.
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        os.environ.setdefault("WATCHFILES_FORCE_POLLING", "true")

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
