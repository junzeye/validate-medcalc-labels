"""
Reproduce Phase 3 Physician Validation Metrics (Table 4 in the ArXiv paper)
=========================================================
This script reproduces Table 1 from the paper, which reports the physician 
validation results from Phase 3 (§3.3). It compares the original MedCalc-Bench 
labels (ŷ_original) and our pipeline-recomputed labels (ŷ_new) against 
ground-truth labels (y*) independently computed by three licensed physicians 
on 50 sampled (C, q) instances.

Data source:
    data/phase3/y_final_and_sampled_MD_evals.xlsx

Metrics computed (matching Table 3):
1. sMAPE (Symmetric Mean Absolute Percentage Error) with bootstrap 95% CI
   - Computed on instances where both y* and ŷ are numeric (non-NA)
2. Agreement count with bootstrap 95% CI
   - Counts how many labels match y* within a clinically reasonable threshold:
     ±5% for continuous values, ±1 for ordinal values (<20), exact match for NA
"""

import re
import pandas as pd
import numpy as np
from typing import Tuple
from pathlib import Path

np.random.seed(42)
PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent

def extract_numeric(value):
    # Extract numeric value from a string, removing units.
    if pd.isna(value) or value == '':
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        if value.strip().upper() == 'N/A':
            return np.nan
        match = re.search(r'-?\d+\.?\d*', value)
        if match:
            return float(match.group())
    return np.nan


def load_data(filepath: Path = None) -> pd.DataFrame:
    """Load the Excel file and return the dataframe.
    
    Args:
        filepath: Path to the Excel file. If None, defaults to 
                  'y_new_and_sampled_MD_evals.xlsx' in phase2_MDs_blind_eval.
    
    Returns:
        DataFrame filtered to only rows with physician labels (exactly 50 rows expected).
        Rows where physician labeled "N/A" (undeterminable) are kept but will have NaN values.
    """
    if filepath is None:
        filepath = PROJECT_ROOT_DIR / 'data' / 'phase2' / 'phase2_MDs_blind_eval' / 'y_new_and_sampled_MD_evals.xlsx'
    
    # Read without automatic NA conversion to distinguish empty cells from "N/A" strings
    df = pd.read_excel(filepath, na_values=[], keep_default_na=False)
    print(f"Loaded {len(df)} rows from {filepath}...")
    
    # Filter to only rows where physician provided input (non-empty cells)
    # This includes both numeric values AND "N/A" (undeterminable)
    physician_col = 'y* (Physician label)'
    df = df[df[physician_col].apply(lambda x: x != '' and not (isinstance(x, float) and pd.isna(x)))].reset_index(drop=True)
    
    # Verify we have exactly 50 rows
    if len(df) != 50:
        raise ValueError(f"Expected exactly 50 rows with physician labels, but got {len(df)}")
    
    # Now convert relevant columns to numeric, extracting values from strings with units
    # "N/A" strings become NaN (undeterminable for calculation purposes)
    numeric_cols = [physician_col, 'y_orig', 'y_new']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(extract_numeric)
    
    return df


def bootstrap_ci(
    data: np.ndarray,
    statistic_func,
    n_bootstrap: int = 10000,
    ci_level: float = 0.95
) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval for a given statistic.
    
    Args:
        data: Array of values to bootstrap
        statistic_func: Function that computes the statistic from data
        n_bootstrap: Number of bootstrap samples
        ci_level: Confidence interval level (default 0.95)
    
    Returns:
        Tuple of (point_estimate, ci_lower, ci_upper)
    """
    n = len(data)
    point_estimate = statistic_func(data)
    
    # Generate bootstrap samples
    bootstrap_stats = []
    for _ in range(n_bootstrap):
        sample_idx = np.random.choice(n, size=n, replace=True)
        sample = data[sample_idx]
        bootstrap_stats.append(statistic_func(sample))
    
    bootstrap_stats = np.array(bootstrap_stats)
    
    # Compute percentile confidence interval
    alpha = 1 - ci_level
    ci_lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
    ci_upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))
    
    return point_estimate, ci_lower, ci_upper


def compute_smape_individual(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Compute individual sMAPE values for each pair.
    
    sMAPE = (2 * |y* - ŷ|) / (|y*| + |ŷ|)
    
    Returns array of individual sMAPE percentages.
    """
    numerator = 2 * np.abs(y_true - y_pred)
    denominator = np.abs(y_true) + np.abs(y_pred)
    
    # Handle division by zero (both y_true and y_pred are 0)
    with np.errstate(divide='ignore', invalid='ignore'):
        smape_vals = np.where(denominator == 0, 0, numerator / denominator)
    
    return smape_vals * 100  # Convert to percentage


def compute_smape_with_bootstrap(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bootstrap: int = 10000
) -> Tuple[float, float, float]:
    """
    Compute sMAPE with bootstrap 95% CI.
    
    sMAPE = (100% / N) * Σ (2 * |y*_i - ŷ_i|) / (|y*_i| + |ŷ_i|)
    
    Skips rows where either value is NaN.
    
    Returns:
        Tuple of (sMAPE%, CI_lower%, CI_upper%)
    """
    # Create mask for valid (non-NaN) pairs
    valid_mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true_valid = y_true[valid_mask]
    y_pred_valid = y_pred[valid_mask]
    
    if len(y_true_valid) == 0:
        return np.nan, np.nan, np.nan
    
    # Compute individual sMAPE values
    smape_vals = compute_smape_individual(y_true_valid, y_pred_valid)
    
    # Bootstrap on the sMAPE values
    return bootstrap_ci(smape_vals, np.mean, n_bootstrap)


def is_ordinal(value: float) -> bool:
    """
    Determine if a single value looks ordinal.
    Ordinal is defined as: <= 20 and looks like an integer.
    """
    if np.isnan(value):
        return False
    # Check if it looks like an integer (within floating point tolerance)
    is_integer_like = np.isclose(value, round(value), atol=1e-9)
    return abs(value) <= 20 and is_integer_like


def is_continuous(value: float) -> bool:
    """
    Determine if a single value looks continuous (not ordinal and not N/A).
    """
    if np.isnan(value):
        return False
    return not is_ordinal(value)


def determine_value_type(y_true: float, y_orig: float, y_new: float) -> str:
    """
    Determine the value type based on all three values.
    
    Logic:
    - If y* is N/A, return 'na'
    - If ANY of the three values is continuous, return 'continuous'
    - Otherwise return 'ordinal'
    """
    if np.isnan(y_true):
        return 'na'
    
    # If at least one value looks continuous, treat as continuous
    if is_continuous(y_true) or is_continuous(y_orig) or is_continuous(y_new):
        return 'continuous'
    
    return 'ordinal'


def check_agreement(y_true: float, y_pred: float, value_type: str) -> bool:
    """
    Check if y_true and y_pred agree according to the criteria:
    1) Both are N/A (NaN)
    2) If continuous: ±5%
    3) If ordinal (<=20 and integer-like): |y* - ŷ| <= 1
    
    Args:
        y_true: Ground truth value
        y_pred: Predicted value
        value_type: 'na', 'ordinal', or 'continuous' (determined externally)
    """
    # Criterion 1: Both are N/A
    if np.isnan(y_true) and np.isnan(y_pred):
        return True
    
    # If one is NaN but not the other, no agreement
    if np.isnan(y_true) or np.isnan(y_pred):
        return False
    
    # Criterion 3: If ordinal
    if value_type == 'ordinal':
        return abs(y_true - y_pred) <= 1
    
    # Criterion 2: If continuous, ±5%
    if y_true == 0:
        # Handle zero case: only agree if y_pred is also 0 or very close
        return abs(y_pred) <= 0.05  # Small tolerance for zero
    else:
        relative_error = abs(y_true - y_pred) / abs(y_true)
        return relative_error <= 0.05


def compute_agreement_fraction_with_bootstrap(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_orig: np.ndarray,
    y_new: np.ndarray,
    n_bootstrap: int = 10000
) -> Tuple[float, float, float, int, int]:
    """
    Compute binary agreement fraction with bootstrap 95% CI.
    
    Args:
        y_true: Ground truth values
        y_pred: Predicted values (either y_orig or y_new)
        y_orig: Original predictions (for determining value type)
        y_new: New predictions (for determining value type)
        n_bootstrap: Number of bootstrap samples
    
    Returns:
        Tuple of (agreement_fraction, CI_lower, CI_upper, n_agree, n_total)
    """
    n = len(y_true)
    
    # Compute agreement for each pair, using all three values to determine type
    agreements = []
    for i in range(n):
        value_type = determine_value_type(y_true[i], y_orig[i], y_new[i])
        agreements.append(check_agreement(y_true[i], y_pred[i], value_type))
    agreements = np.array(agreements).astype(float)
    
    n_agree = int(np.sum(agreements))
    n_total = n
    
    # Bootstrap on the agreement indicators
    point_est, ci_lower, ci_upper = bootstrap_ci(agreements, np.mean, n_bootstrap)
    
    return point_est, ci_lower, ci_upper, n_agree, n_total


def print_separator(char: str = '=', length: int = 70):
    """Print a separator line."""
    print(char * length)


def main():
    """Main function to run all analyses."""
    
    print("Loading data from y_new_and_sampled_MD_evals.xlsx...")
    df = load_data()
    y_true = df['y* (Physician label)'].values
    y_orig = df['y_orig'].values
    y_new = df['y_new'].values
    
    print(f"Rows with physician labels: {len(df)}")
    print(f"Rows with non-NaN y_orig: {np.sum(~np.isnan(y_orig))}")
    print(f"Rows with non-NaN y_new: {np.sum(~np.isnan(y_new))}")
    print()
    
    # Compute valid pairs for each comparison
    valid_orig = np.sum(~(np.isnan(y_true) | np.isnan(y_orig)))
    valid_new = np.sum(~(np.isnan(y_true) | np.isnan(y_new)))
    
    print_separator()
    print("1. SYMMETRIC MEAN ABSOLUTE PERCENTAGE ERROR (sMAPE) ANALYSIS")
    print_separator()
    print()
    
    print("Formula: sMAPE = (100%/N) × Σ (2×|y* - ŷ|) / (|y*| + |ŷ|)")
    print()
    
    smape_orig, smape_orig_ci_low, smape_orig_ci_high = compute_smape_with_bootstrap(y_true, y_orig)
    print(f"sMAPE for y_orig:")
    print(f"  Valid pairs (excluding N/A): {valid_orig}")
    print(f"  sMAPE = {smape_orig:.4f}%")
    print(f"  95% Bootstrap CI: [{smape_orig_ci_low:.4f}%, {smape_orig_ci_high:.4f}%]")
    print()
    
    smape_new, smape_new_ci_low, smape_new_ci_high = compute_smape_with_bootstrap(y_true, y_new)
    print(f"sMAPE for y_new:")
    print(f"  Valid pairs (excluding N/A): {valid_new}")
    print(f"  sMAPE = {smape_new:.4f}%")
    print(f"  95% Bootstrap CI: [{smape_new_ci_low:.4f}%, {smape_new_ci_high:.4f}%]")
    print()
    
    print_separator()
    print("2. BINARY AGREEMENT FRACTION ANALYSIS")
    print_separator()
    print()
    
    print("Agreement criteria:")
    print("  1) Both y* and ŷ are N/A")
    print("  2) If continuous (any of y*, y_orig, y_new is continuous): |y* - ŷ| / |y*| ≤ 5%")
    print("  3) If ordinal (all values ≤20 and integer-like): |y* - ŷ| ≤ 1")
    print()
    
    agree_orig, agree_orig_ci_low, agree_orig_ci_high, n_agree_orig, n_total = \
        compute_agreement_fraction_with_bootstrap(y_true, y_orig, y_orig, y_new)
    print(f"Agreement fraction for y_orig:")
    print(f"  Agreements: {n_agree_orig} / {n_total}")
    print(f"  Agreement Fraction = {agree_orig:.4f} ({agree_orig*100:.2f}%)")
    print(f"  95% Bootstrap CI: [{agree_orig_ci_low:.4f}, {agree_orig_ci_high:.4f}] "
          f"({agree_orig_ci_low*100:.2f}%, {agree_orig_ci_high*100:.2f}%)")
    print()
    
    agree_new, agree_new_ci_low, agree_new_ci_high, n_agree_new, n_total = \
        compute_agreement_fraction_with_bootstrap(y_true, y_new, y_orig, y_new)
    print(f"Agreement fraction for y_new:")
    print(f"  Agreements: {n_agree_new} / {n_total}")
    print(f"  Agreement Fraction = {agree_new:.4f} ({agree_new*100:.2f}%)")
    print(f"  95% Bootstrap CI: [{agree_new_ci_low:.4f}, {agree_new_ci_high:.4f}] "
          f"({agree_new_ci_low*100:.2f}%, {agree_new_ci_high*100:.2f}%)")
    print()
    
    print_separator()
    print("DETAILED AGREEMENT BREAKDOWN")
    print_separator()
    print()
    
    print("Row-by-row agreement analysis:")
    print("-" * 90)
    print(f"{'Row':<5} {'y* (ground truth)':<20} {'y_orig':<15} {'y_new':<15} {'Agree_orig':<12} {'Agree_new':<12}")
    print("-" * 90)
    
    for i in range(len(df)):
        yt = y_true[i]
        yo = y_orig[i]
        yn = y_new[i]
        
        yt_str = "N/A" if np.isnan(yt) else f"{yt:.4f}"
        yo_str = "N/A" if np.isnan(yo) else f"{yo:.4f}"
        yn_str = "N/A" if np.isnan(yn) else f"{yn:.4f}"
        
        value_type = determine_value_type(yt, yo, yn)
        
        agree_o = check_agreement(yt, yo, value_type)
        agree_n = check_agreement(yt, yn, value_type)
        
        agree_o_str = "✓" if agree_o else "✗"
        agree_n_str = "✓" if agree_n else "✗"
        
        type_str = f"({value_type})"
        
        print(f"{i:<5} {yt_str:<20} {yo_str:<15} {yn_str:<15} {agree_o_str:<12} {agree_n_str:<12} {type_str}")
    
    print("-" * 90)
    print()
    
    print_separator()
    print("SUMMARY TABLE")
    print_separator()
    print()
    
    # Create summary table
    print(f"{'Metric':<25} {'y_orig':<30} {'y_new':<30}")
    print("-" * 85)
    print(f"{'sMAPE (%)':<25} {smape_orig:.2f} [{smape_orig_ci_low:.2f}, {smape_orig_ci_high:.2f}]"
          f"{'':>8}{smape_new:.2f} [{smape_new_ci_low:.2f}, {smape_new_ci_high:.2f}]")
    print(f"{'Agreement Fraction':<25} {agree_orig:.4f} [{agree_orig_ci_low:.4f}, {agree_orig_ci_high:.4f}]"
          f"{'':>5}{agree_new:.4f} [{agree_new_ci_low:.4f}, {agree_new_ci_high:.4f}]")
    print("-" * 85)


if __name__ == "__main__":
    main()

