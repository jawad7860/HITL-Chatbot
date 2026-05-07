from fastapi import APIRouter

from app.api.routes import chat, decision, status

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(decision.router)
api_router.include_router(status.router)

__all__ = ["api_router"]
