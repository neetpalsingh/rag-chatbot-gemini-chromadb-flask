import logging
from fastapi import APIRouter, HTTPException

from database import ChromaManager
from database.local_db import LocalDatabase
from models import HealthResponse, StatsResponse, StatsData

logger = logging.getLogger(__name__)

router = APIRouter()

chroma_manager = ChromaManager()
local_db = LocalDatabase()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        success=True,
        message="Service is running"
    )

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    try:
        count = local_db.get_total_chunks()
        return StatsResponse(
            success=True,
            data=StatsData(total_chunks=count)
        )
    except Exception as e:
        logger.exception(f'Failed to get stats: {e}')
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )
