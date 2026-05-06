from fastapi import APIRouter
from app.core.config import get_settings
router = APIRouter(tags=["system"])

@router.get("/health")
async def health(): return {"status": "healthy", "app": get_settings().APP_NAME}

@router.get("/")
async def root(): return {"app": get_settings().APP_NAME, "version": get_settings().APP_VERSION, "docs": "/docs"}
