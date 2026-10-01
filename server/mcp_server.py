from fastmcp import FastMCP
from server.core.models import (ProblemSearchFilters,InnovationProcessFilters, CrieyaPreincubationHubQARequest, CrieyaFocusQARequest, TrlLevelRequest)
from server.core.services import (get_problem_statements,get_innovation_process, get_crieya_preincubation_hub_qa, get_crieya_focus_qa, get_trl_levels)
import asyncio
mcp = FastMCP(name="crieya-chatbot")

@mcp.tool()
async def search_problem_statements_tool(filters: ProblemSearchFilters):
    """
    Search SIH problem statements.

    Examples:
    - "farming related technology bucket"
    - "problem with ID SIH1524"
    - "AI problems from ISRO"
    - "problem id 1524"

    Supports:
    - Exact ID matching
    - Partial matching across other fields

    ID Handling:
    - If the query contains a 4-digit number referring to a problem ID
    (e.g., "id 1524", "problem 1524", "problem statement 1524"),
    automatically prepend "SIH" to the number
    → Example: 1524 → SIH1524

    - If "SIH" is already present, use the ID as-is

    Notes:
    - ID matching is exact after normalization
    - Other fields are matched partially
    """

    response = await asyncio.to_thread(
        get_problem_statements,
        filters
    )
    return response.model_dump()

@mcp.tool()
async def innovation_process_tool(filters: InnovationProcessFilters):
    """
    Retrieve CRiEYA innovation process data and annexures.

    Supports:
    - Fetching a specific innovation process by:
        • Process number (e.g., 1, 2, 3...)

    - Retrieving the full innovation process:
        • Returns all processes with complete details when requested

    - Listing all innovation process titles

    - Retrieving annexure-related information:
        • Supports Annexures A through J
        • If a query mentions an annexure (e.g., "Annexure A", "Annexure D"),
        return all relevant details and associated data

    - Combined queries:
        • Handles queries that reference both process data and annexures
        • Example: "Process 2 with Annexure B"
    """
    response = await asyncio.to_thread(
        get_innovation_process,
        filters
    )
    return response.model_dump()

@mcp.tool()
async def crieya_preincubation_hub_qa_tool(request:CrieyaPreincubationHubQARequest):
    """
    Answer questions about CRiEYA as an institution:
    identity, affiliation, funding, impact, programs, patents, startups.
    """
    response = await asyncio.to_thread(
        get_crieya_preincubation_hub_qa,
        request
    )
    return response.model_dump()

@mcp.tool()
async def crieya_focus_tool(request: CrieyaFocusQARequest):
    """
    Answer questions about CRiEYA focus areas:
    domains, technologies, practice areas, objectives.
    """
    response = await asyncio.to_thread(
        get_crieya_focus_qa,
        request
    )
    return response.model_dump()

@mcp.tool()
async def trl_levels_tool(request: TrlLevelRequest):
    """
    Provide information on Technology Readiness Levels (TRL):
    definitions, criteria, etc.
    """
    response = await asyncio.to_thread(
        get_trl_levels,
        request
    )
    return response.model_dump()

if __name__ == "__main__":
    import os
    mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
    mcp_port = int(os.getenv("MCP_PORT", "9000"))
    # SSE transport (HTTP server)
    mcp.run(
        transport="sse",
        host=mcp_host,
        port=mcp_port
    )