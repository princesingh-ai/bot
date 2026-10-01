from app.config import settings
from sarvamai import SarvamAI
from app.utils.logger import get_logger

logger = get_logger(__name__)

client = None
if settings.SARVAM_API_KEY:
    try:
        client = SarvamAI(api_subscription_key=settings.SARVAM_API_KEY)
        logger.info("Successfully initialized SarvamAI client.")
    except Exception as error:
        logger.error(f"Failed to initialize SarvamAI client: {error}")
        client = None
else:
    logger.warning("SARVAM_API_KEY is not configured in environment. LLM calls will fail until set.")


def chat(messages, tools=None):
    global client
    if not client and settings.SARVAM_API_KEY:
        try:
            client = SarvamAI(api_subscription_key=settings.SARVAM_API_KEY)
        except Exception as e:
            logger.error(f"Lazy initialization of SarvamAI client failed: {e}")

    if not client:
        logger.error("SarvamAI client is not initialized.")
        raise RuntimeError("SarvamAI client is not initialized. Ensure SARVAM_API_KEY is set in environment.")

    kwargs = {
        "model": "sarvam-105b",
        "messages": messages,
    }

    if tools:
        kwargs["tools"] = tools

    logger.info(f"Sending chat completion request to SarvamAI model {kwargs['model']}")
    try:
        response = client.chat.completions(**kwargs)
        logger.info("Received response from SarvamAI.")
        return response
    except Exception as error:
        logger.error(f"Error during chat completion with SarvamAI: {error}")
        raise error