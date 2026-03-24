from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.endpoints import health, search, rag, translate
from app.services.embedding_service import get_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the model
    print(f"🚀 Starting {settings.PROJECT_NAME}...")
    get_model()
    yield
    # Shutdown
    print(f"👋 Shutting down {settings.PROJECT_NAME}...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Semantic search and RAG-based Q&A for Marathi documents",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])
app.include_router(translate.router, prefix="/translate", tags=["Translate"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "/search",
            "ask": "/rag/ask",
            "translate": "/translate",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=9999, reload=True)
