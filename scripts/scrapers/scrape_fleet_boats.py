#!/usr/bin/env python3
"""
GitHub Actions compatible version of fleetBoats.py
This script checks for existing boats_fleet22.json data in the data directory.
If it exists, it uses that. If not, it uses a fallback approach.
"""
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import load_json, save_json
from utils.path_utils import BOATS_FILE, PROJECT_ROOT

# Setup logging
logger = setup_logger(__name__)

# Payment fields to preserve from existing data (simplified format)
PAYMENT_FIELDS = [
    'Fleet Dues',
    'Class Dues'
]

def get_existing_fleet_data():
    """Try to load existing boats_fleet22.json data if available"""
    if BOATS_FILE.exists():
        try:
            data = load_json(BOATS_FILE)
            logger.info(f"Loaded {len(data)} boat entries from existing file: {BOATS_FILE}")
            return data
        except Exception as e:
            logger.error(f"Error loading existing fleet data: {str(e)}")
    
    return None

def extract_payment_data(existing_data):
    """Extract payment data from existing boats data."""
    payment_map = {}
    if existing_data:
        for boat in existing_data:
            hull = str(boat.get('Hull Number', ''))
            if hull:
                payment_map[hull] = {field: boat.get(field, '') for field in PAYMENT_FIELDS}
        logger.info(f"Extracted payment data for {len(payment_map)} boats")
    return payment_map

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
            boat['Fleet Dues'] = 'Not Paid'
            boat['Class Dues'] = 'Not Paid'
    
    logger.info(f"Merged payment data for {merged_count} boats")
    return scraped_data

def try_load_from_members_html():
    """Try to load data from members.html file"""
    try:
        # Look for members.html in pages or project root
        members_pages = PROJECT_ROOT / 'pages' / 'members.html'
        members_root = PROJECT_ROOT / 'members.html'
        
        file_path = members_pages if members_pages.exists() else members_root
        
        if not file_path.exists():
            logger.warning(f"members.html not found at: {file_path}")
            return None
            
        with open(file_path, 'r') as file:
            html_content = file.read()
            
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', {'class': 'table table-striped'})
        
        if table is None:
            logger.warning("Could not find the table with class 'table table-striped'")
            return None
        
        data_list = []
        headers = [header.text.strip() for header in table.find_all('th')]
        
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) == len(headers):
                row_data = {headers[i]: col.text.strip() for i, col in enumerate(cols)}
                data_list.append(row_data)
        
        logger.info(f"Extracted {len(data_list)} boat entries from members.html")
        return data_list
    
    except Exception as e:
        logger.error(f"Error processing members.html: {str(e)}")
        return None

def generate_fallback_data():
    """Generate fallback data"""
    # This is just a minimal structure to allow the workflow to continue
    logger.warning("Using fallback data generation")
    return [
        {"Hull Number": "Unavailable", "Boat Name": "Data Unavailable", "Owner": "N/A"}
    ]

def main():
    """Main execution function."""
    logger.info("Starting fleet boats scraper")
    
    # Load existing data to preserve payment information
    existing_data = get_existing_fleet_data()
    payment_map = extract_payment_data(existing_data)
    
    # Try different methods to get fresh boat list
    fresh_data = try_load_from_members_html()
    
    if fresh_data:
        # Merge fresh data with existing payment data
        data = merge_payment_data(fresh_data, payment_map)
        logger.info("Updated boat list with preserved payment data")
    elif existing_data:
        # Use existing data if we can't get fresh data
        data = existing_data
        logger.info("Using existing boat data (no updates available)")
    else:
        # Last resort fallback
        data = generate_fallback_data()
        logger.warning("Using fallback data")
    
    # Save the data
    save_json(data, BOATS_FILE)
    logger.info(f"Successfully processed {len(data)} boat entries")
    paid_count = len([b for b in data if b.get('Fleet Dues') == 'Paid'])
    print(f"Successfully processed {len(data)} boat entries and saved to {BOATS_FILE}")
    print(f"Preserved payment data: {paid_count} paid boats")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        raise