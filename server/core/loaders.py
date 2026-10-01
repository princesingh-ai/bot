import pandas as pd
import yaml
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Base directory is the project root (3 levels up from server/core/loaders.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"

if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"Configuration file not found at: {CONFIG_PATH}. Ensure config.yaml is in project root.")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as file_handle:
        application_config = yaml.safe_load(file_handle) or {}
    logger.info(f"Successfully loaded config from {CONFIG_PATH}")
except Exception as error:
    logger.critical(f"Failed to parse configuration from {CONFIG_PATH}: {error}")
    raise RuntimeError(f"Failed to parse config.yaml: {error}") from error


def _resolve_path(path_str: str | None) -> Path:
    if not path_str:
        raise ValueError("Dataset path is missing from config.yaml")
    p = Path(path_str)
    if not p.is_absolute():
        p = BASE_DIR / p
    return p


def load_problem_statements() -> pd.DataFrame:
    """Load and normalize SIH problem statements from Excel."""
    config = application_config.get("data", {}).get("problem_statements", {})
    file_path = _resolve_path(config.get("path"))
    if not file_path.exists():
        raise FileNotFoundError(f"Required dataset file not found: {file_path}. Ensure data files exist.")
    
    sheet_name = config.get("sheet", "Worksheet")
    try:
        dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
        logger.info(f"Successfully loaded problem statements data from {file_path}.")
        return dataframe.rename(columns={
            "Problem Creater's Organization": "organization",
            "Technology Bucket": "technology_bucket",
            "Category": "category",
            "Description": "description",
            "Title": "title",
            "ID": "problem_id",
        })
    except Exception as error:
        logger.critical(f"Failed to read problem statements Excel at {file_path}: {error}")
        raise RuntimeError(f"Error loading problem statements from {file_path}: {error}") from error


def load_innovation_process() -> pd.DataFrame:
    """Load innovation process steps from Excel."""
    config = application_config.get("data", {}).get("innovation_process", {})
    file_path = _resolve_path(config.get("path"))
    if not file_path.exists():
        raise FileNotFoundError(f"Required dataset file not found: {file_path}. Ensure data files exist.")

    sheet_name = config.get("sheet", "template")
    try:
        dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
        logger.info(f"Successfully loaded innovation process data from {file_path}.")
        return dataframe.rename(columns={
            "Unnamed: 0": "process_no",
            "Unnamed: 1": "process_title",
            "Inputs": "input",
            "Process": "process",
            "Output": "output",
        })
    except Exception as error:
        logger.critical(f"Failed to read innovation process Excel at {file_path}: {error}")
        raise RuntimeError(f"Error loading innovation process from {file_path}: {error}") from error


def load_crieya_preincubation_hub() -> str:
    """Load CRIEYA pre-incubation hub text data."""
    config = application_config.get("data", {}).get("crieya_preincubation_hub", {})
    file_path = _resolve_path(config.get("path"))
    if not file_path.exists():
        raise FileNotFoundError(f"Required dataset file not found: {file_path}. Ensure data files exist.")
    try:
        content = file_path.read_text(encoding="utf-8")
        logger.info(f"Successfully loaded crieya preincubation hub data from {file_path}.")
        return content
    except Exception as error:
        logger.critical(f"Failed to read CRIEYA pre-incubation hub file at {file_path}: {error}")
        raise RuntimeError(f"Error reading {file_path}: {error}") from error


def load_crieya_focus() -> str:
    """Load CRIEYA focus areas text."""
    config = application_config.get("data", {}).get("crieya_focus", {})
    file_path = _resolve_path(config.get("path"))
    if not file_path.exists():
        raise FileNotFoundError(f"Required dataset file not found: {file_path}. Ensure data files exist.")
    try:
        content = file_path.read_text(encoding="utf-8")
        logger.info(f"Successfully loaded crieya focus data from {file_path}.")
        return content
    except Exception as error:
        logger.critical(f"Failed to read CRIEYA focus file at {file_path}: {error}")
        raise RuntimeError(f"Error reading {file_path}: {error}") from error


def load_trl_levels() -> str:
    """Load Technology Readiness Levels (TRL) text."""
    config = application_config.get("data", {}).get("trl_levels", {})
    file_path = _resolve_path(config.get("path"))
    if not file_path.exists():
        raise FileNotFoundError(f"Required dataset file not found: {file_path}. Ensure data files exist.")
    try:
        content = file_path.read_text(encoding="utf-8")
        logger.info(f"Successfully loaded trl levels data from {file_path}.")
        return content
    except Exception as error:
        logger.critical(f"Failed to read TRL levels file at {file_path}: {error}")
        raise RuntimeError(f"Error reading {file_path}: {error}") from error