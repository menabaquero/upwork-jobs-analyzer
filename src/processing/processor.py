"""
Data Processing Module
----------------------
This module takes cleaned data and prepares it for analysis.
It standardizes columns, creates simple derived features,
and saves the processed dataset.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main processing function.
    
    Args:
        df: Cleaned pandas DataFrame
        
    Returns:
        Processed and analysis-ready DataFrame
    """
    logger.info("Starting data processing...")
    
    df_processed = df.copy()
    
    # 1. Standardize column names
    df_processed = standardize_column_names(df_processed)
    
    # 2. Basic cleaning / type conversion
    df_processed = clean_and_convert_types(df_processed)
    
    # 3. Create simple derived columns
    df_processed = create_derived_columns(df_processed)
    
    # 4. Save processed data
    save_processed_data(df_processed)
    
    logger.info(f"Processing completed. Final shape: {df_processed.shape}")
    return df_processed


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names: lowercase + underscores + strip spaces."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w_]", "", regex=True)
    )
    logger.info(f"Standardized columns: {df.columns.tolist()}")
    return df


def clean_and_convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Basic type conversion and cleaning."""
    
    # Example: clean the Rate column if it exists
    if "rate" in df.columns:
        # Keep original and create a simple numeric version if possible
        df["rate_clean"] = (
            df["rate"]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
        )
        df["rate_clean"] = pd.to_numeric(df["rate_clean"], errors="coerce")
        logger.info("Created 'rate_clean' numeric column")
    
    # Convert Posted Date if possible
    if "posted_date" in df.columns:
        df["posted_date"] = pd.to_datetime(df["posted_date"], errors="coerce")
        logger.info("Converted 'posted_date' to datetime")
    
    return df


def create_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Create simple useful derived columns."""
    
    # Is hourly job?
    if "job_type" in df.columns:
        df["is_hourly"] = df["job_type"].astype(str).str.lower().str.contains("hourly")
        logger.info("Created 'is_hourly' column")
    
    # Number of skills
    if "skills_required" in df.columns:
        df["skills_count"] = (
            df["skills_required"]
            .astype(str)
            .apply(lambda x: len([s.strip() for s in x.split(",") if s.strip()]) if pd.notna(x) else 0)
        )
        logger.info("Created 'skills_count' column")
    
    return df


def save_processed_data(df: pd.DataFrame, filename: str = "upwork_jobs_processed.csv") -> None:
    """Save the processed DataFrame to data/processed/."""
    output_path = PROCESSED_DATA_DIR / filename
    df.to_csv(output_path, index=False)
    logger.info(f"Processed data saved to: {output_path}")


# ======================
# Test the full flow
# ======================
if __name__ == "__main__":
    from src.collection.file_collector import load_csv
    from src.cleaning.cleaner import clean_data, print_cleaning_report
    
    print("1. Loading data...")
    df_raw = load_csv()
    
    print("\n2. Cleaning data...")
    df_cleaned, report = clean_data(df_raw)
    print_cleaning_report(report)
    
    print("3. Processing data...")
    df_processed = process_data(df_cleaned)
    
    print("\nProcessed data preview:")
    print(df_processed.head(3))
    print(f"\nColumns: {df_processed.columns.tolist()}")   