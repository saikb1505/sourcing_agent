from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.routes import auth_router, search_router, admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown."""
    # Startup
    init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.APP_NAME,
    description="A sourcing agent application for finding professionals via LinkedIn search",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(search_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Sourcing Agent API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
