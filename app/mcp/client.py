import asyncio
from typing import Optional
from fastmcp import Client
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MCPClientManager:
    """
    Resilient client manager for the FastMCP backend service.
    Handles startup connection, lazy reconnection, concurrent requests,
    and graceful shutdown.
    """

    def __init__(self):
        self._client: Optional[Client] = None
        self._lock = asyncio.Lock()
        self._is_closing = False

    async def _connect_client(self) -> Client:
        logger.info(f"Connecting to FastMCP server at {settings.MCP_SERVER_URL}...")
        client = Client(settings.MCP_SERVER_URL)
        await client.__aenter__()
        logger.info("Successfully established connection to FastMCP server.")
        return client

    async def get_client(self) -> Client:
        """
        Thread/coroutine safe retrieval of active MCP client.
        Automatically reconnects if not initialized or previously disconnected.
        """
        if self._client is not None and not self._is_closing:
            return self._client

        async with self._lock:
            if self._client is not None and not self._is_closing:
                return self._client

            max_retries = settings.MCP_MAX_RETRIES
            backoff = 0.5
            last_error: Optional[Exception] = None

            for attempt in range(1, max_retries + 1):
                try:
                    self._client = await self._connect_client()
                    return self._client
                except Exception as err:
                    last_error = err
                    logger.warning(
                        f"Failed connection attempt {attempt}/{max_retries} to FastMCP server: {err}"
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(backoff)
                        backoff = min(backoff * 2, 5.0)

            raise RuntimeError(
                f"FastMCP server at {settings.MCP_SERVER_URL} is unreachable after {max_retries} attempts: {last_error}"
            ) from last_error

    async def init(self) -> Client:
        """Explicit startup initialization."""
        return await self.get_client()

    async def is_healthy(self) -> bool:
        """Verify FastMCP backend connectivity and ping response."""
        if self._is_closing:
            return False
        try:
            client = await self.get_client()
            return await client.ping()
        except Exception as e:
            logger.warning(f"FastMCP health check failed: {e}")
            return False

    async def reconnect(self) -> Client:
        """Safely discard current client and establish a fresh connection."""
        async with self._lock:
            await self._disconnect_unsafe()
            self._client = await self._connect_client()
            return self._client

    async def _disconnect_unsafe(self):
        if self._client is not None:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception as err:
                logger.error(f"Error during FastMCP client disconnect: {err}")
            finally:
                self._client = None

    async def close(self):
        """Clean shutdown of client resources."""
        self._is_closing = True
        async with self._lock:
            logger.info("Closing FastMCP client connection...")
            await self._disconnect_unsafe()
            logger.info("FastMCP client connection closed.")


# Global singleton instance
_manager = MCPClientManager()


async def init_mcp_client() -> Client:
    return await _manager.init()


async def close_mcp_client():
    await _manager.close()


async def get_mcp_client() -> Client:
    return await _manager.get_client()


async def check_mcp_health() -> bool:
    return await _manager.is_healthy()
