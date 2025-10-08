import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

# Keywords indicating a sail replacement/defect exempt from limits
REPLACEMENT_KEYWORDS = {"replacement", "replaced", "destroyed", "defective"}

def load_data(file_path):
    """Load JSON sail tags into a DataFrame and parse dates."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['Delivery Date'] = pd.to_datetime(df['Delivery Date'], errors='coerce')
    df = df.dropna(subset=['Delivery Date'])
    df['Year'] = df['Delivery Date'].dt.year
    # Exclude hull 0 (sailmaker entries)
    df = df[df['Hull'] != '0']
    return df

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
        description="Analyze sail purchase records for class-rule violations."
    )
    parser.add_argument(
        'input_file',
        type=Path,
        help="Path to sail_tags.json file"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help="Optional CSV file to write violations to"
    )
    args = parser.parse_args()

    df = load_data(args.input_file)
    violations = analyze_limits(df)

    if violations.empty:
        print("No violations found (excluding Hull 0).")
    else:
        print("Violations detected (excluding Hull 0):")
        print(violations.to_string(index=False))

        if args.output:
            violations.to_csv(args.output, index=False)
            print(f"\nViolations written to: {args.output}")

if __name__ == "__main__":
    main()
 