"""
Data Cleaning Module
--------------------
This module cleans the Upwork jobs dataset.
It handles duplicates, missing values, outliers, and basic PII detection.
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import Tuple, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Main cleaning function.
    
    Args:
        df: Raw pandas DataFrame
        
    Returns:
        cleaned_df: Cleaned DataFrame
        report: Dictionary with cleaning statistics
    """
    logger.info("Starting data cleaning...")
    
    report = {
        "original_rows": len(df),
        "original_columns": len(df.columns),
        "duplicate_rows_removed": 0,
        "duplicate_columns_removed": 0,
        "missing_values_found": 0,
        "outliers_found": 0,
        "pii_found": 0
    }
    
    df_clean = df.copy()
    
    # 1. Remove duplicate rows
    df_clean, dup_rows = remove_duplicate_rows(df_clean)
    report["duplicate_rows_removed"] = dup_rows
    
    # 2. Remove duplicate columns
    df_clean, dup_cols = remove_duplicate_columns(df_clean)
    report["duplicate_columns_removed"] = dup_cols
    
    # 3. Handle missing values
    df_clean, missing_count = handle_missing_values(df_clean)
    report["missing_values_found"] = missing_count
    
    # 4. Detect outliers (basic)
    outliers = detect_outliers(df_clean)
    report["outliers_found"] = outliers
    
    # 5. Detect basic PII
    pii_count = detect_pii(df_clean)
    report["pii_found"] = pii_count
    
    report["final_rows"] = len(df_clean)
    report["final_columns"] = len(df_clean.columns)
    
    logger.info("Data cleaning completed.")
    return df_clean, report


def remove_duplicate_rows(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """Remove fully duplicated rows."""
    initial = len(df)
    df = df.drop_duplicates()
    removed = initial - len(df)
    logger.info(f"Removed {removed} duplicate rows")
    return df, removed


def remove_duplicate_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """Remove duplicated columns."""
    initial = len(df.columns)
    df = df.loc[:, ~df.columns.duplicated()]
    removed = initial - len(df.columns)
    logger.info(f"Removed {removed} duplicate columns")
    return df, removed


def handle_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Identify and handle missing values.
    For now we only report them. You can later decide to drop or fill.
    """
    missing_count = df.isnull().sum().sum()
    logger.info(f"Found {missing_count} missing values")
    
    # Example: show missing values per column
    missing_per_column = df.isnull().sum()
    missing_per_column = missing_per_column[missing_per_column > 0]
    if not missing_per_column.empty:
        logger.info("Missing values per column:")
        for col, count in missing_per_column.items():
            logger.info(f"  - {col}: {count}")
    
    return df, int(missing_count)


def detect_outliers(df: pd.DataFrame) -> int:
    """
    Very basic outlier detection using IQR for numeric columns.
    Currently only counts them.
    """
    numeric_cols = df.select_dtypes(include=np.number).columns
    outlier_count = 0
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        outlier_count += len(outliers)
    
    logger.info(f"Found {outlier_count} potential outliers in numeric columns")
    return outlier_count


def detect_pii(df: pd.DataFrame) -> int:
    """
    Very simple PII detection (emails and phone numbers).
    """
    pii_count = 0
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"\+?\d[\d\s\-]{8,}\d"
    
    text_cols = df.select_dtypes(include="object").columns
    
    for col in text_cols:
        # Emails
        emails = df[col].astype(str).str.contains(email_pattern, na=False).sum()
        # Phones
        phones = df[col].astype(str).str.contains(phone_pattern, na=False).sum()
        pii_count += emails + phones
    
    logger.info(f"Found {pii_count} potential PII values")
    return int(pii_count)


def print_cleaning_report(report: Dict[str, Any]) -> None:
    """Pretty print the cleaning report."""
    print("\n" + "="*50)
    print("DATA CLEANING REPORT")
    print("="*50)
    for key, value in report.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("="*50 + "\n")


# ======================
# Simple test
# ======================
if __name__ == "__main__":
    from src.collection.file_collector import load_csv
    
    print("Loading data...")
    df_raw = load_csv()
    
    print("\nCleaning data...")
    df_cleaned, report = clean_data(df_raw)
    
    print_cleaning_report(report)
    
    print("Cleaned data preview:")
    print(df_cleaned.head(3))