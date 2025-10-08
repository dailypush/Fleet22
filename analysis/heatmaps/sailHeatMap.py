#!/usr/bin/env python3
"""
Sail Purchase Heatmap Generator for Fleet22_us repository
Generates heatmaps showing sail purchases by hull, year, sail type, and sailmaker.
"""
import sys
import argparse
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from utils.logger import setup_logger
from utils.data_loader import load_json
from utils.path_utils import PROJECT_ROOT

# Setup logging
logger = setup_logger('heatmap_generator', PROJECT_ROOT / 'logs' / 'analysis.log')

def load_sail_data(file_path):
    """Load and prepare sail data for analysis."""
    try:
        logger.info(f"Loading sail data from {file_path}")
        df = pd.read_json(file_path)
        
        # Convert "Delivery Date" to datetime and "Fleet" to string for proper filtering
        df["Delivery Date"] = pd.to_datetime(df["Delivery Date"], errors='coerce')
        df = df.dropna(subset=["Delivery Date"])  # Drop rows where 'Delivery Date' is NaT
        df["Fleet"] = df["Fleet"].astype(str)
        
        logger.info(f"Loaded {len(df)} sail records")
        return df
        
    except Exception as e:
        logger.error(f"Error loading sail data: {e}")
        raise

def filter_fleet_data(df, fleet_number='22'):
    """Filter data for a specific fleet."""
    fleet_data = df[df['Fleet'] == fleet_number]
    logger.info(f"Found {len(fleet_data)} records for Fleet {fleet_number}")
    return fleet_data

def generate_hull_heatmap(hull_data, hull_number, output_dir):
    """Generate and save a heatmap for a specific hull."""
    try:
        # Group by year, sail type, and sailmaker
        hull_purchases = hull_data.groupby([
            hull_data['Delivery Date'].dt.year,
            'Sail Type',
            'Sailmaker'
        ]).size().unstack(level=[1, 2], fill_value=0)
        
        hull_purchases.columns = [' '.join(col).strip() for col in hull_purchases.columns.values]
        
        # Create the heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            hull_purchases.T,
            cmap="YlGnBu",
            annot=True,
            fmt="d",
            cbar_kws={'label': 'Number of Purchases'}
        )
        plt.title(f'Purchases for Hull {hull_number} by Year, Sail Type, and Sailmaker')
        plt.xlabel('Year')
        plt.ylabel('Sail Type and Sailmaker')
        plt.tight_layout()
        
        # Save the heatmap
        file_path = output_dir / f'hull_{hull_number}_heatmap.png'
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved heatmap for Hull {hull_number}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error generating heatmap for Hull {hull_number}: {e}")
        plt.close()
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Generate sail purchase heatmaps for Fleet 22 hulls"
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=PROJECT_ROOT / 'data' / 'sails' / 'sail_tags.json',
        help="Path to sail_tags.json file"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent / 'heatmaps',
        help="Output directory for heatmap images"
    )
    parser.add_argument(
        '--fleet',
        type=str,
        default='22',
        help="Fleet number to analyze (default: 22)"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help="Limit number of hulls to process (default: all)"
    )
    parser.add_argument(
        '--hulls',
        nargs='+',
        type=str,
        help="Specific hull numbers to process (e.g., --hulls 10 128 144)"
    )
    args = parser.parse_args()
    
    try:
        logger.info("Starting heatmap generation...")
        
        # Load sail data
        df = load_sail_data(args.input)
        
        # Filter for specific fleet
        fleet_data = filter_fleet_data(df, args.fleet)
        
        if len(fleet_data) == 0:
            logger.warning(f"No data found for Fleet {args.fleet}")
            print(f"⚠️  No data found for Fleet {args.fleet}")
            return 1
        
        # Get unique hulls
        if args.hulls:
            unique_hulls = [h for h in args.hulls if h in fleet_data['Hull'].astype(str).values]
            logger.info(f"Processing specified hulls: {unique_hulls}")
        else:
            unique_hulls = fleet_data['Hull'].unique()
            if args.limit:
                unique_hulls = unique_hulls[:args.limit]
                logger.info(f"Limited to first {args.limit} hulls")
        
        # Create output directory
        args.output.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {args.output}")
        
        # Generate heatmaps
        print(f"Generating heatmaps for {len(unique_hulls)} hulls...")
        generated_files = []
        
        for hull in tqdm(unique_hulls, desc="Generating Heatmaps"):
            hull_data = fleet_data[fleet_data['Hull'] == hull]
            if len(hull_data) > 0:
                file_path = generate_hull_heatmap(hull_data, hull, args.output)
                generated_files.append(file_path)
        
        # Summary
        print(f"\n✅ Successfully generated {len(generated_files)} heatmaps")
        print(f"📁 Saved to: {args.output}")
        logger.info(f"Completed heatmap generation: {len(generated_files)} files")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during heatmap generation: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
