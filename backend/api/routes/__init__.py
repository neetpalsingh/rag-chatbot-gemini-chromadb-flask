from api.routes.upload import router as upload_router
from api.routes.chat import router as chat_router
from api.routes.health import router as health_router

__all__ = ['upload_router', 'chat_router', 'health_router']
