from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router as chat_router
from app.config import settings
from app.mcp.client import init_mcp_client, close_mcp_client, check_mcp_health
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up CRIEYA Assistant FastAPI application...")
    try:
        await init_mcp_client()
        logger.info("Startup connection to FastMCP backend established successfully.")
    except Exception as exc:
        logger.critical(
            f"Unable to connect to FastMCP server during startup: {exc}. "
            "FastAPI will start, but endpoints requiring MCP will return 503 until MCP is reachable."
        )

    yield

    logger.info("Shutting down CRIEYA Assistant FastAPI application...")
    await close_mcp_client()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production FastAPI backend for CRIEYA Pre-Incubation Hub AI",
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

# Configure CORS
allow_all_origins = "*" in settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(chat_router, prefix="/api/v1")


@app.get("/health/live", tags=["Health"], summary="Liveness probe")
def liveness():
    """Returns 200 if the FastAPI application process is alive."""
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"], summary="Readiness probe")
@app.get("/health", tags=["Health"], summary="Overall health check")
async def health_check():
    """
    Checks overall service health including connection to the FastMCP backend service.
    Returns 200 if all components are healthy, or 503 degraded if dependencies fail.
    """
    mcp_healthy = await check_mcp_health()
    status_code = status.HTTP_200_OK if mcp_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if mcp_healthy else "degraded",
            "mcp_connected": mcp_healthy,
            "version": settings.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )
