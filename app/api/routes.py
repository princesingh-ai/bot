from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import ChatRequest, ChatResponse
from app.guard.guard import validate_input
from app.agent.agent import run_agent
from app.dependencies import get_mcp
from fastmcp import Client
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


async def validate_chat_request(request: ChatRequest) -> ChatRequest:
    """Validate query against length limits and prompt injection before backend invocation."""
    error_msg = await validate_input(request.query)
    if error_msg:
        logger.warning(f"Rejecting chat request due to guardrail validation failure: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    return request


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest = Depends(validate_chat_request),
    mcp_client: Client = Depends(get_mcp),
):
    logger.info(f"Processing API chat request: {request.query}")
    try:
        response_text = await run_agent(request.query, mcp_client)
        return ChatResponse(response=response_text)
    except Exception as exc:
        logger.error(f"Error processing agent query: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Agent service error: {exc}"
        )
