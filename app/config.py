import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project root and load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "CRIEYA Assistant API"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # FastMCP service configuration
    MCP_HOST: str = os.getenv("MCP_HOST", "127.0.0.1")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "9000"))
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", f"http://{MCP_HOST}:{MCP_PORT}/sse")
    MCP_CONNECT_TIMEOUT_SECONDS: float = float(os.getenv("MCP_CONNECT_TIMEOUT_SECONDS", "30.0"))
    MCP_MAX_RETRIES: int = int(os.getenv("MCP_MAX_RETRIES", "5"))

    # LLM & AI configuration
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    MAX_QUERY_LENGTH: int = int(os.getenv("MAX_QUERY_LENGTH", "2000"))

    # CORS configuration
    _cors_raw: str = os.getenv("CORS_ORIGINS", "*")
    if _cors_raw.strip() == "*":
        CORS_ORIGINS: list[str] = ["*"]
    else:
        CORS_ORIGINS: list[str] = [orig.strip() for orig in _cors_raw.split(",") if orig.strip()]

settings = Settings()
