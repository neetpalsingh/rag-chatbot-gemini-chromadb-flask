"""
Production startup script for FastAPI application with Uvicorn.
Supports multiple workers and proper logging configuration.
"""

import os
from pathlib import Path

if __name__ == "__main__":
    import uvicorn

    workers = int(os.getenv("WORKERS", "2"))

    workers = max(1, min(workers, 4))

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        log_config=None,
        access_log=True
    )
