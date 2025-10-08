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
from utils.data_loader import save_json, load_json
from utils.path_utils import PROJECT_ROOT, BOATS_FILE, ensure_directories

# Setup logging
logger = setup_logger('local_scraper', PROJECT_ROOT / 'logs' / 'scraping.log')

# Payment fields to preserve from existing data
PAYMENT_FIELDS = [
    'Owner',
    'Contact Email',
    'Fleet Dues 2025',
    'Fleet Dues Payment Date',
    'Fleet Dues Payment Method',
    'Class Dues 2025',
    'Class Dues Payment Date',
    'Notes'
]

def load_existing_payment_data():
    """Load existing payment data to preserve it during scraping."""
    try:
        if BOATS_FILE.exists():
            existing_data = load_json(BOATS_FILE)
            # Create a mapping of hull number -> payment data
            payment_map = {}
            for boat in existing_data:
                hull = str(boat.get('Hull Number', ''))
                if hull:
                    payment_map[hull] = {field: boat.get(field, '') for field in PAYMENT_FIELDS}
            logger.info(f"Loaded existing payment data for {len(payment_map)} boats")
            return payment_map
        return {}
    except Exception as e:
        logger.warning(f"Could not load existing payment data: {e}")
        return {}

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

def merge_payment_data(scraped_data, payment_map):
    """Merge scraped boat data with existing payment information."""
    merged_count = 0
    for boat in scraped_data:
        hull = str(boat.get('Hull Number', ''))
        if hull in payment_map:
            # Preserve existing payment data
            boat.update(payment_map[hull])
            merged_count += 1
        else:
            # Initialize payment fields for new boats
            for field in PAYMENT_FIELDS:
                if field not in boat:
                    if 'Dues' in field and 'Date' not in field and 'Method' not in field:
                        boat[field] = 'Unpaid' if 'Fleet' in field else 'Unknown'
                    else:
                        boat[field] = ''
    
    logger.info(f"Merged payment data for {merged_count} boats")
    return scraped_data

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
        
        # Load existing payment data to preserve it
        logger.info("Loading existing payment data...")
        payment_map = load_existing_payment_data()
        
        # Scrape the data
        boats_data = scrape_local_fleet_boats(args.input)
        
        # Merge with existing payment data
        boats_data = merge_payment_data(boats_data, payment_map)
        
        # Save the data (automatic backup via save_json)
        save_json(boats_data, args.output)
        
        print(f"✅ Successfully processed {len(boats_data)} boat entries")
        print(f"📄 Saved to {args.output}")
        print(f"💾 Preserved payment data for {len([b for b in boats_data if b.get('Fleet Dues 2025') == 'Paid'])} paid boats")
        
        logger.info(f"Local scraper completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during local scraping: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
