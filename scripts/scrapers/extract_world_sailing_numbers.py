#!/usr/bin/env python3
"""
World Sailing Numbers Extractor for Fleet22_us repository
Extracts crew names and World Sailing numbers from HTML files.
"""
import sys
import argparse
import json
from pathlib import Path
from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.path_utils import PROJECT_ROOT

# Setup logging
logger = setup_logger('ws_numbers_extractor', PROJECT_ROOT / 'logs' / 'scraping.log')

def extract_sailing_data(html_file_path):
    """
    Extract crew names and World Sailing numbers from an HTML file.
    
    Args:
        html_file_path: Path to the HTML file to parse
        
    Returns:
        List of dictionaries with crew_name and ws_number keys
    """
    try:
        logger.info(f"Reading HTML file: {html_file_path}")
        
        # Open and read the HTML file
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Initialize an empty list to store the crew names and World Sailing numbers
        sailing_data = []

        # Find all rows in the table (assuming data is within table rows)
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            # Check if the row has enough cells and contains a link in the expected position
            if len(cells) > 4 and cells[4].find('a'):
                crew_name = cells[1].text.strip()
                world_sailing_number = cells[4].find('a').text.strip()
                sailing_data.append({
                    'crew_name': crew_name,
                    'ws_number': world_sailing_number
                })

        logger.info(f"Extracted {len(sailing_data)} World Sailing numbers")
        return sailing_data
        
    except Exception as e:
        logger.error(f"Error extracting sailing data: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Extract crew names and World Sailing numbers from HTML files"
    )
    parser.add_argument(
        'input',
        type=Path,
        help="Path to HTML file containing World Sailing data"
    )
    parser.add_argument(
        '--output',
        type=Path,
        help="Optional output JSON file path"
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'text'],
        default='text',
        help="Output format (default: text)"
    )
    args = parser.parse_args()
    
    try:
        # Check if input file exists
        if not args.input.exists():
            raise FileNotFoundError(f"Input file not found: {args.input}")
        
        # Extract the data
        data = extract_sailing_data(args.input)
        
        if not data:
            logger.warning("No World Sailing numbers found in the file")
            print("⚠️  No World Sailing numbers found")
            return 0
        
        # Output the data based on format
        if args.format == 'json':
            output = json.dumps(data, indent=2)
            print(output)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(output)
                logger.info(f"Saved JSON to {args.output}")
                
        elif args.format == 'csv':
            print("Crew Name,World Sailing Number")
            for item in data:
                print(f"{item['crew_name']},{item['ws_number']}")
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with open(args.output, 'w') as f:
                    f.write("Crew Name,World Sailing Number\n")
                    for item in data:
                        f.write(f"{item['crew_name']},{item['ws_number']}\n")
                logger.info(f"Saved CSV to {args.output}")
                
        else:  # text format
            for item in data:
                print(f"Crew Name: {item['crew_name']}, World Sailing Number: {item['ws_number']}")
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with open(args.output, 'w') as f:
                    for item in data:
                        f.write(f"Crew Name: {item['crew_name']}, World Sailing Number: {item['ws_number']}\n")
                logger.info(f"Saved text to {args.output}")
        
        print(f"\n✅ Successfully extracted {len(data)} World Sailing numbers")
        if args.output:
            print(f"📄 Saved to {args.output}")
        
        logger.info("Extraction completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
