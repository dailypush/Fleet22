#!/usr/bin/env python3
"""
Sailmaker trends analysis for Fleet22_us repository
Analyzes and visualizes sail purchase trends by sailmaker over time.
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.path_utils import PROJECT_ROOT, SAILS_FILE

# Setup logging
logger = setup_logger('sailmaker_analysis', PROJECT_ROOT / 'logs' / 'scraping.log')

def load_sail_data(file_path):
    """Load sail tags data from JSON file."""
    try:
        df = pd.read_json(file_path)
        logger.info(f"Loaded {len(df)} sail records from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading sail data: {e}")
        raise

def analyze_sailmaker_trends(df, sailmakers=None, output_path=None):
    """Analyze and visualize sailmaker purchase trends."""
    if sailmakers is None:
        sailmakers = ['Quantum', 'North', 'Ullman']
    
    # Filter for specified sailmakers
    filtered_data = df[df['Sailmaker'].isin(sailmakers)].copy()
    logger.info(f"Analyzing {len(filtered_data)} records for sailmakers: {', '.join(sailmakers)}")
    
    # Ensure 'Delivery Date' is in datetime format
    filtered_data['Delivery Date'] = pd.to_datetime(filtered_data['Delivery Date'], errors='coerce')
    filtered_data = filtered_data.dropna(subset=['Delivery Date'])
    
    # Extract year
    filtered_data['Year'] = filtered_data['Delivery Date'].dt.year
    
    # Group by year and sailmaker, then count purchases
    annual_purchases = filtered_data.groupby(['Year', 'Sailmaker']).size().unstack(fill_value=0)
    
    # Log summary statistics
    logger.info(f"Analysis period: {annual_purchases.index.min()} - {annual_purchases.index.max()}")
    for sailmaker in sailmakers:
        if sailmaker in annual_purchases.columns:
            total = annual_purchases[sailmaker].sum()
            logger.info(f"{sailmaker}: {total} total purchases")
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 7))
    annual_purchases.plot(kind='area', stacked=False, alpha=0.5, ax=ax)
    ax.set_title('Annual Sail Purchases by Sailmaker (Area Chart)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Sails Purchased', fontsize=12)
    ax.legend(title='Sailmaker', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Save the plot
    if output_path is None:
        output_path = PROJECT_ROOT / 'scripts' / 'analysis' / 'SailMakerPurchaseTrend.png'
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Chart saved to {output_path}")
    print(f"✅ Chart saved to {output_path}")
    
    # Display summary
    print(f"\n📊 Sailmaker Purchase Summary:")
    print(f"Period: {annual_purchases.index.min()} - {annual_purchases.index.max()}")
    print("\nTotal Purchases:")
    for sailmaker in sailmakers:
        if sailmaker in annual_purchases.columns:
            total = annual_purchases[sailmaker].sum()
            print(f"  {sailmaker}: {total}")
    
    return annual_purchases

def main():
    parser = argparse.ArgumentParser(
        description="Analyze sail purchase trends by sailmaker"
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=SAILS_FILE,
        help=f"Path to sail_tags.json file (default: {SAILS_FILE})"
    )
    parser.add_argument(
        '--sailmakers',
        nargs='+',
        default=['Quantum', 'North', 'Ullman'],
        help="List of sailmakers to analyze (default: Quantum North Ullman)"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help="Output path for the chart image"
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help="Display the chart in addition to saving it"
    )
    args = parser.parse_args()
    
    try:
        logger.info("Starting sailmaker trends analysis...")
        
        # Load data
        df = load_sail_data(args.input)
        
        # Analyze trends
        results = analyze_sailmaker_trends(df, args.sailmakers, args.output)
        
        # Optionally display the chart
        if args.show:
            plt.show()
        
        logger.info("Analysis completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
