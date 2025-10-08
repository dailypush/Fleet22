#!/usr/bin/env python3
"""
Local fleet boats scraper for Fleet22_us repository
Scrapes boat data from a local members.html file.
"""
import sys
import argparse
from pathlib import Path
from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import save_json
from utils.path_utils import PROJECT_ROOT, BOATS_FILE, ensure_directories

# Setup logging
logger = setup_logger('local_scraper', PROJECT_ROOT / 'logs' / 'scraping.log')

def scrape_local_fleet_boats(html_file_path):
    """Scrape boat data from a local HTML file."""
    try:
        # Log attempt to read the file
        logger.info(f"Attempting to read file: {html_file_path}")
        
        # Load the HTML content from the file
        with open(html_file_path, 'r') as file:
            html_content = file.read()
            
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the table by class name
        table = soup.find('table', {'class': 'table table-striped'})
        
        if table is None:
            raise ValueError("Could not find the table with class 'table table-striped'")
        
        # Extract data
        data_list = []
        
        # Assuming the first row of the table is headers
        headers = [header.text.strip() for header in table.find_all('th')]
        logger.info(f"Found headers: {headers}")
        
        # Process each row of the table
        for row in table.find_all('tr')[1:]:  # skip the header row
            cols = row.find_all('td')
            if len(cols) == len(headers):  # Make sure the row has the expected number of columns
                row_data = {headers[i]: col.text.strip() for i, col in enumerate(cols)}
                data_list.append(row_data)
        
        logger.info(f"Successfully processed {len(data_list)} boat entries")
        return data_list
        
    except Exception as e:
        logger.error(f"Error processing fleet boats data: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Scrape fleet boats data from a local HTML file"
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=PROJECT_ROOT / 'pages' / 'members.html',
        help="Path to members.html file (default: pages/members.html)"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=BOATS_FILE,
        help=f"Output JSON file path (default: {BOATS_FILE})"
    )
    args = parser.parse_args()
    
    try:
        logger.info("Starting local fleet boats scraper...")
        
        # Check if input file exists
        if not args.input.exists():
            # Try alternate location
            alt_path = PROJECT_ROOT / 'members.html'
            if alt_path.exists():
                args.input = alt_path
                logger.info(f"Using alternate path: {alt_path}")
            else:
                raise FileNotFoundError(f"Could not find members.html at {args.input} or {alt_path}")
        
        # Ensure directories exist
        ensure_directories()
        
        # Scrape the data
        boats_data = scrape_local_fleet_boats(args.input)
        
        # Save the data (automatic backup via save_json)
        save_json(boats_data, args.output)
        
        print(f"✅ Successfully processed {len(boats_data)} boat entries")
        print(f"📄 Saved to {args.output}")
        
        logger.info(f"Local scraper completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during local scraping: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
