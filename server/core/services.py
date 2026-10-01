import pandas as pd
from server.core.models import (
    ProblemSearchFilters, ProblemSearchResponse,
    InnovationProcessFilters, InnovationProcessResponse,
    CrieyaPreincubationHubQARequest, CrieyaPreincubationHubQAResponse,
    CrieyaFocusQARequest, CrieyaFocusQAResponse,
    TrlLevelRequest, TrlLevelResponse
)
from server.core.loaders import (
    load_problem_statements, 
    load_innovation_process, 
    load_crieya_preincubation_hub, 
    load_crieya_focus, 
    load_trl_levels
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Load datasets 
logger.info("Initializing datasets in services...")
PROBLEM_STATEMENTS_DATAFRAME = load_problem_statements()
INNOVATION_PROCESS_DATAFRAME = load_innovation_process()
CRIEYA_HUB_DOCUMENT = load_crieya_preincubation_hub()
CRIEYA_FOCUS_DOCUMENT = load_crieya_focus()
TRL_LEVELS_DOCUMENT = load_trl_levels()

def get_problem_statements(filters: ProblemSearchFilters) -> ProblemSearchResponse:
    """
    Search SIH problem statements using optional filters.
    Exact match is used for problem_id, others are partial and case-insensitive.
    Allows combinations of multiple filters.
    """
    logger.info(f"Searching problem statements with filters: {filters}")
    try:
        dataframe = PROBLEM_STATEMENTS_DATAFRAME.copy()
        
        if dataframe.empty:
            logger.warning("Problem statements dataframe is empty.")
            return ProblemSearchResponse(count=0, results=[])

        # Filter by exact problem ID match
        if filters.problem_id:
            dataframe = dataframe[dataframe["problem_id"].astype(str).str.strip().str.upper() == filters.problem_id.strip().upper()]

        # Filter by title
        if filters.title:
            dataframe = dataframe[dataframe["title"].astype(str).str.contains(filters.title, case=False, na=False)]

        # Filter by technology bucket
        if filters.technology_bucket:
            dataframe = dataframe[dataframe["technology_bucket"].astype(str).str.contains(filters.technology_bucket, case=False, na=False)]

        # Filter by category
        if filters.category:
            dataframe = dataframe[dataframe["category"].astype(str).str.contains(filters.category, case=False, na=False)]

        # Filter by description
        if filters.description:
            dataframe = dataframe[dataframe["description"].astype(str).str.contains(filters.description, case=False, na=False)]
        
        # filter by organization
        if filters.organization:
            dataframe = dataframe[dataframe["organization"].astype(str).str.contains(filters.organization, case=False, na=False)]

        # Fill NaNs to ensure valid JSON serialization
        dataframe = dataframe.fillna("")

        # Convert filtered DataFrame into list of dictionaries
        records = dataframe.to_dict(orient="records")

        logger.info(f"Found {len(records)} problem statements matching filters.")
        # Return structured response
        return ProblemSearchResponse(
            count=len(records),
            results=records
        )
    except Exception as error:
        logger.error(f"Error during problem statements search: {error}")
        return ProblemSearchResponse(count=0, results=[])


def get_innovation_process(filters: InnovationProcessFilters) -> InnovationProcessResponse:
    """
    Retrieve innovation process data, allowing combinations of filters
    like specific process_no and specific fields.
    """
    logger.info(f"Retrieving innovation process with filters: {filters}")
    try:
        dataframe = INNOVATION_PROCESS_DATAFRAME.copy()

        if dataframe.empty:
            logger.warning("Innovation process dataframe is empty.")
            return InnovationProcessResponse(count=0, results=[])

        # Filter by specific process number
        if filters.process_no is not None:
            dataframe = dataframe[dataframe["process_no"] == filters.process_no]

        # Return only stages if requested and no specific field is targeted
        if filters.stages is True and filters.field is None:
            if "process_no" in dataframe.columns and "process_title" in dataframe.columns:
                dataframe = dataframe[["process_no", "process_title"]]
        
        # Filter by specific field
        elif filters.field == "title":
            dataframe = dataframe[["process_no", "process_title"]]
        elif filters.field == "input":
            dataframe = dataframe[["process_no", "input"]]
        elif filters.field == "process":
            dataframe = dataframe[["process_no", "process"]]
        elif filters.field == "output":
            dataframe = dataframe[["process_no", "output"]]

        # Fill NaNs to ensure valid JSON serialization
        dataframe = dataframe.fillna("")

        records = dataframe.to_dict(orient="records")
        logger.info(f"Returned {len(records)} innovation process records.")
        
        return InnovationProcessResponse(
            count=len(records),
            results=records
        )
    except Exception as error:
        logger.error(f"Error retrieving innovation process: {error}")
        return InnovationProcessResponse(count=0, results=[])


def get_crieya_preincubation_hub_qa(request: CrieyaPreincubationHubQARequest) -> CrieyaPreincubationHubQAResponse:
    """
    Return CRIEYA pre-incubation hub information.
    """
    logger.info(f"Fetching CRIEYA pre-incubation hub QA for request: {request.question}")
    return CrieyaPreincubationHubQAResponse(answer=CRIEYA_HUB_DOCUMENT, source="Crieya Pre-Incubation Hub Document")


def get_crieya_focus_qa(request: CrieyaFocusQARequest) -> CrieyaFocusQAResponse:
    """
    Return CRIEYA focus areas and technologies.
    """
    logger.info(f"Fetching CRIEYA focus QA for request: {request.question}")
    return CrieyaFocusQAResponse(
        answer=CRIEYA_FOCUS_DOCUMENT,
        source="CRiEYA Focus Document"
    )

def get_trl_levels(request: TrlLevelRequest) -> TrlLevelResponse:
    """
    Return Technology Readiness Level (TRL) definitions.
    """
    logger.info(f"Fetching TRL levels for request: {request.question}")
    return TrlLevelResponse(
        answer=TRL_LEVELS_DOCUMENT,
        source="TRL Levels Document"
    )