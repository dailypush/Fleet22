#!/usr/bin/env python3
"""
Sail purchase limits validator for Fleet22_us repository
Analyzes sail purchase records against J/105 class rules.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.path_utils import PROJECT_ROOT, SAILS_FILE

# Setup logging
logger = setup_logger('sail_limits', PROJECT_ROOT / 'logs' / 'scraping.log')

# Keywords indicating a sail replacement/defect exempt from limits
REPLACEMENT_KEYWORDS = {"replacement", "replaced", "destroyed", "defective"}

def load_data(file_path):
    """Load JSON sail tags into a DataFrame and parse dates."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} sail tags from {file_path}")
        df = pd.DataFrame(data)
        df['Delivery Date'] = pd.to_datetime(df['Delivery Date'], errors='coerce')
        df = df.dropna(subset=['Delivery Date'])
        df['Year'] = df['Delivery Date'].dt.year
        # Exclude hull 0 (sailmaker entries)
        df = df[df['Hull'] != '0']
        logger.info(f"Processing {len(df)} valid sail entries (excluding Hull 0)")
        return df
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise

def is_replacement(note):
    """Determine if a sail entry is a replacement/exempt based on notes."""
    if not isinstance(note, str):
        return False
    note_lower = note.lower()
    return any(kw in note_lower for kw in REPLACEMENT_KEYWORDS)

def analyze_limits(df):
    """Analyze sail purchases against class rules and return violations."""
    # Flag replacements
    df['IsReplacement'] = df['Notes'].apply(is_replacement)
    # Filter out replacements
    valid = df[~df['IsReplacement']].copy()

    violations = []

    for hull, group in valid.groupby('Hull'):
        # Determine first use year for extra sail allowance
        first_year = group['Year'].min()
        # Count sails per year
        yearly = group.groupby('Year').size().to_dict()

        # Check per-year violations
        for year, count in yearly.items():
            allowed = 2 + (1 if year == first_year else 0)
            if count > allowed:
                violations.append({
                    'Hull': hull,
                    'Year': year,
                    'Count': count,
                    'Allowed': allowed,
                    'Violation': 'Yearly limit exceeded'
                })

        # Check two-year rolling-window violations (allowed = 3)
        years = sorted(yearly)
        for y in years:
            count_two_year = yearly.get(y, 0) + yearly.get(y + 1, 0)
            if count_two_year > 3:
                violations.append({
                    'Hull': hull,
                    'Year': f'{y}-{y+1}',
                    'Count': count_two_year,
                    'Allowed': 3,
                    'Violation': 'Two-year limit exceeded'
                })

    return pd.DataFrame(violations)

def main():
    parser = argparse.ArgumentParser(
        description="Analyze sail purchase records for J/105 class-rule violations."
    )
    parser.add_argument(
        'input_file',
        type=Path,
        nargs='?',
        default=SAILS_FILE,
        help=f"Path to sail_tags.json file (default: {SAILS_FILE})"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help="Optional CSV file to write violations to"
    )
    args = parser.parse_args()

    logger.info(f"Starting sail limits analysis...")
    
    try:
        df = load_data(args.input_file)
        violations = analyze_limits(df)

        if violations.empty:
            print("✅ No violations found (excluding Hull 0).")
            logger.info("No sail limit violations detected")
        else:
            print("⚠️  Violations detected (excluding Hull 0):")
            print(violations.to_string(index=False))
            logger.warning(f"Found {len(violations)} sail limit violations")

            if args.output:
                violations.to_csv(args.output, index=False)
                print(f"\n📄 Violations written to: {args.output}")
                logger.info(f"Violations report saved to {args.output}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during sail limits analysis: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
 