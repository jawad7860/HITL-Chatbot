"""FastAPI application entry point.

The async SQLite checkpointer is opened during startup (via lifespan) and
closed on shutdown. The compiled graph and ChatService are stashed on
``app.state`` so route handlers can pull them via dependency injection.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.api import api_router
from app.core import get_settings
from app.graph import build_graph
from app.services import ChatService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open checkpointer, build graph, expose service. Cleanup on shutdown."""
    settings = get_settings()

    # Ensure the checkpoint dir exists
    db_path = Path(settings.checkpoint_db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Opening checkpointer at %s", db_path)
    async with AsyncSqliteSaver.from_conn_string(str(db_path)) as checkpointer:
        graph = build_graph(checkpointer)
        app.state.graph = graph
        app.state.chat_service = ChatService(graph)
        logger.info("Graph compiled and ready")
        yield
        logger.info("Shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="HITL Chatbot",
        description="Memory-enabled chatbot with LangGraph + Human-in-the-Loop tool approval.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/health", tags=["meta"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=bool(int(os.getenv("RELOAD", "0"))),
    )
