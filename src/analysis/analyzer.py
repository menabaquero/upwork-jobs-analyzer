
"""
Data Analysis Module
--------------------
This module generates the first insights from the processed Upwork jobs data:
- Summary statistics
- Experience level & Job type distribution
- Top skills demand
- Simple correlations
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Main analysis function.
    
    Args:
        df: Processed pandas DataFrame
        
    Returns:
        Dictionary containing all analysis results
    """
    logger.info("Starting data analysis...")
    
    results = {}
    
    # 1. Basic Summary
    results["summary"] = generate_summary(df)
    
    # 2. Distributions
    results["experience_distribution"] = get_value_counts(df, "experience_level")
    results["job_type_distribution"] = get_value_counts(df, "job_type")
    
    # 3. Top Skills
    results["top_skills"] = get_top_skills(df)
    
    # 4. Correlation (numeric columns only)
    results["correlation"] = get_correlation(df)
    
    # 5. Save results
    save_analysis_results(results)
    
    logger.info("Analysis completed successfully.")
    return results


def generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate high-level summary statistics."""
    summary = {
        "total_jobs": len(df),
        "unique_job_titles": df["job_title"].nunique() if "job_title" in df.columns else 0,
        "average_skills_per_job": round(df["skills_count"].mean(), 2) if "skills_count" in df.columns else None,
        "hourly_jobs_percentage": round(df["is_hourly"].mean() * 100, 1) if "is_hourly" in df.columns else None,
    }
    
    if "rate_clean" in df.columns:
        summary["average_rate"] = round(df["rate_clean"].mean(), 2)
        summary["median_rate"] = round(df["rate_clean"].median(), 2)
        summary["min_rate"] = df["rate_clean"].min()
        summary["max_rate"] = df["rate_clean"].max()
    
    logger.info("Summary statistics generated")
    return summary


def get_value_counts(df: pd.DataFrame, column: str) -> pd.Series:
    """Get value counts for a categorical column."""
    if column not in df.columns:
        return pd.Series(dtype=int)
    
    counts = df[column].value_counts(dropna=False)
    logger.info(f"Distribution for '{column}' created")
    return counts


def get_top_skills(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Extract and count the most demanded skills.
    """
    if "skills_required" not in df.columns:
        return pd.DataFrame()
    
    all_skills = []
    
    for skills in df["skills_required"].dropna():
        # Split by common separators
        skill_list = [s.strip() for s in str(skills).replace(";", ",").split(",")]
        all_skills.extend([s for s in skill_list if s and s.lower() != "nan"])
    
    skill_counts = Counter(all_skills)
    top_skills = pd.DataFrame(skill_counts.most_common(top_n), columns=["skill", "count"])
    
    logger.info(f"Top {top_n} skills extracted")
    return top_skills


def get_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate correlation matrix for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.shape[1] < 2:
        logger.info("Not enough numeric columns for correlation")
        return pd.DataFrame()
    
    corr = numeric_df.corr().round(3)
    logger.info("Correlation matrix calculated")
    return corr


def save_analysis_results(results: Dict[str, Any]) -> None:
    """Save key analysis results to the outputs folder."""
    
    # Save Top Skills
    if "top_skills" in results and not results["top_skills"].empty:
        results["top_skills"].to_csv(OUTPUTS_DIR / "top_skills.csv", index=False)
        logger.info("Saved: outputs/top_skills.csv")
    
    # Save Correlation
    if "correlation" in results and not results["correlation"].empty:
        results["correlation"].to_csv(OUTPUTS_DIR / "correlation_matrix.csv")
        logger.info("Saved: outputs/correlation_matrix.csv")
    
    # Save Summary as a simple text/csv
    summary_df = pd.DataFrame([results.get("summary", {})])
    summary_df.to_csv(OUTPUTS_DIR / "summary_report.csv", index=False)
    logger.info("Saved: outputs/summary_report.csv")


def print_analysis_report(results: Dict[str, Any]) -> None:
    """Pretty print the main insights."""
    print("\n" + "="*60)
    print("UPWORK JOBS - ANALYSIS REPORT")
    print("="*60)
    
    print("\n--- SUMMARY ---")
    for key, value in results.get("summary", {}).items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n--- EXPERIENCE LEVEL DISTRIBUTION ---")
    print(results.get("experience_distribution", "N/A"))
    
    print("\n--- JOB TYPE DISTRIBUTION ---")
    print(results.get("job_type_distribution", "N/A"))
    
    print("\n--- TOP SKILLS ---")
    print(results.get("top_skills", "N/A").head(10))
    
    print("\n" + "="*60)


# ======================
# Full pipeline test
# ======================
if __name__ == "__main__":
    from src.collection.file_collector import load_csv
    from src.cleaning.cleaner import clean_data
    from src.processing.processor import process_data
    
    print("1. Loading data...")
    df_raw = load_csv()
    
    print("\n2. Cleaning data...")
    df_cleaned, _ = clean_data(df_raw)
    
    print("\n3. Processing data...")
    df_processed = process_data(df_cleaned)
    
    print("\n4. Analyzing data...")
    results = analyze_data(df_processed)
    
    print_analysis_report(results)