

"""
File-based Data Collection Module
---------------------------------
This module is responsible for loading Upwork jobs data 
from local files (CSV and JSON).
"""

import pandas as pd
from pathlib import Path
import logging

# Configure simple logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Base path of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def load_csv(filename: str = "upwork_jobs_sample.csv") -> pd.DataFrame:
    """
    Load jobs data from a CSV file.
    
    Args:
        filename: Name of the CSV file inside data/raw/
        
    Returns:
        pandas DataFrame with the jobs data
    """
    file_path = RAW_DATA_DIR / filename

    try:
        df = pd.read_csv(file_path)
        logger.info(f"CSV loaded successfully – {len(df)} rows from {filename}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise


def load_json(filename: str = "upwork_jobs_sample.json") -> pd.DataFrame:
    """
    Load jobs data from a JSON file.
    
    Args:
        filename: Name of the JSON file inside data/raw/
        
    Returns:
        pandas DataFrame with the jobs data
    """
    file_path = RAW_DATA_DIR / filename

    try:
        df = pd.read_json(file_path)
        logger.info(f"JSON loaded successfully – {len(df)} rows from {filename}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading JSON: {e}")
        raise


# Simple test when running this file directly
if __name__ == "__main__":
    print("Testing File Collector...\n")

    # Test CSV
    df_csv = load_csv()
    print("CSV columns:", df_csv.columns.tolist())
    print(df_csv.head(2))
    print("-" * 50)

    # Test JSON
    df_json = load_json()
    print("JSON columns:", df_json.columns.tolist())
    print(df_json.head(2))