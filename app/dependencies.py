from app.mcp.client import get_mcp_client
from fastapi import Request, HTTPException
from fastmcp import Client
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def get_mcp(request: Request) -> Client:
    """FastAPI dependency to inject an active FastMCP client instance."""
    try:
        return await get_mcp_client()
    except Exception as exc:
        logger.error(f"Failed to acquire MCP client for request: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Backend MCP server is currently unavailable. Please try again shortly."
        )
