import json
import asyncio
from app.llm.sarvam_client import chat
from app.utils.logger import get_logger
from app.agent.prompts import SYSTEM_PROMPT

logger = get_logger(__name__)

MAX_QUERY_LENGTH = 2000

async def run_agent(query: str, mcp_client):
    logger.info(f"Starting agent run for query: {query}")
    
    if len(query) > MAX_QUERY_LENGTH:
        logger.warning(f"Security: Query rejected. Exceeds maximum length of {MAX_QUERY_LENGTH} characters.")
        return f"Error: Your query is too long. Please restrict it to {MAX_QUERY_LENGTH} characters or less."

    try:
        # Get tools from MCP
        mcp_tools = await mcp_client.list_tools()
        logger.info(f"Fetched {len(mcp_tools)} tools from MCP server.")

        tools_list = []
        for tool in mcp_tools:
            tools_list.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })

        # Prompt wrapping: Strongly bind the constraint to the user message to prevent deviation
        strict_user_query = (
            f"User Query:\n{query}\n\n"
            "---\n"
            "CRITICAL SYSTEM INSTRUCTION: Evaluate the user query above. If it is NOT specifically asking about "
            "CRIEYA, Pre-Incubation, Technology Readiness Levels (TRL), or SIH (Smart India Hackathon) Problem Statements, "
            "you MUST refuse to answer. Do not use any tools. Return EXACTLY this phrase and nothing else: "
            "'I am specialized only in CRIEYA and SIH topics. I cannot answer that question.'"
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": strict_user_query}
        ]

        MAX_ITERATIONS = 5
        for iteration in range(MAX_ITERATIONS):
            logger.info(f"Calling LLM chat interface (Iteration {iteration + 1}/{MAX_ITERATIONS})...")
            response = await asyncio.to_thread(chat, messages, tools_list)
            message = response.choices[0].message

            # add assistant message
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": message.tool_calls
            })

            # if no tool call → return answer
            if not message.tool_calls:
                logger.info("No more tool calls required. Returning final answer from agent.")
                return message.content

            # execute tools
            for tool_call in message.tool_calls:
                logger.info(f"Executing tool call: {tool_call.function.name}")
                try:
                    result = await mcp_client.call_tool(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments)
                    )

                    texts = [content.text for content in result.content if getattr(content, "type", None) == "text"]
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": "\n".join(texts)
                    })
                    logger.info(f"Successfully executed tool call: {tool_call.function.name}")
                except Exception as tool_error:
                    logger.error(f"Error executing tool {tool_call.function.name}: {tool_error}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": f"Error executing tool: {tool_error}"
                    })

        logger.warning(f"Security fallback: Agent reached maximum iterations ({MAX_ITERATIONS}) without a final answer. Execution halted.")
        return f"Error: I've reached my processing limit ({MAX_ITERATIONS} thinking steps) and had to stop."
        
    except Exception as agent_error:
        logger.critical(f"Critical error during agent execution: {agent_error}")
        raise RuntimeError(f"Agent execution failure: {agent_error}") from agent_error