"""FastAPI dependency providers."""
from fastapi import Request
from app.services import ChatService


def get_chat_service(request: Request) -> ChatService:
    """Returns the ChatService instance built during app startup (lifespan)."""
    return request.app.state.chat_service
