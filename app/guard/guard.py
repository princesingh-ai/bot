import re
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Basic static blocklist for prompt injection terms
PROMPT_INJECTION_KEYWORDS = [
    r"ignore previous instructions",
    r"disregard previous instructions",
    r"you are now",
    r"system prompt",
    r"forget what i told you",
    r"ignore all instructions"
]

async def validate_input(query: str) -> str | None:
    """
    Validates user query constraints using robust limits and static keyword blocklists.
    Returns an error message if invalid, else None.
    """
    if len(query) > settings.MAX_QUERY_LENGTH:
        logger.warning(f"Security: Query rejected. Exceeds max length of {settings.MAX_QUERY_LENGTH}.")
        return f"Error: Your query is too long. Please restrict it to {settings.MAX_QUERY_LENGTH} characters or less."

    query_lower = query.lower()
    for pattern in PROMPT_INJECTION_KEYWORDS:
        if re.search(pattern, query_lower):
            logger.warning(f"Security: Query rejected due to suspected prompt injection.")
            return "Security Error: Your query contains disallowed commands or prompt override attempts."

    return None
