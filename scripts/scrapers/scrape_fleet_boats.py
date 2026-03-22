#!/usr/bin/env python3
"""
Fleet 22 boat data builder.
Loads Fleet 22 boats from j105_members_status.json (filtering by Fleet == "22"),
merges with existing boats_fleet22.json to preserve payment and yacht club data.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import load_json, save_json
from utils.path_utils import BOATS_FILE, MEMBERS_FILE

# Setup logging
logger = setup_logger(__name__)

# Fields to preserve from existing data (manually maintained)
PRESERVE_FIELDS = [
    'Fleet Dues',
    'Class Dues',
    'Yacht Club'
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

def extract_preserved_data(existing_data):
    """Extract payment and yacht club data from existing boats data, keyed by hull number."""
    preserved_map = {}
    if existing_data:
        for boat in existing_data:
            hull = str(boat.get('Hull Number', ''))
            if hull:
                preserved_map[hull] = {field: boat.get(field, '') for field in PRESERVE_FIELDS}
        logger.info(f"Extracted preserved data for {len(preserved_map)} boats")
    return preserved_map

def merge_preserved_data(scraped_data, preserved_map):
    """Merge scraped boat data with existing payment and yacht club information."""
    merged_count = 0
    for boat in scraped_data:
        hull = str(boat.get('Hull Number', ''))
        if hull in preserved_map:
            existing = preserved_map[hull]
            # Preserve Fleet Dues (manually maintained — never overwrite)
            boat['Fleet Dues'] = existing.get('Fleet Dues', 'Not Paid')
            # Preserve Class Dues
            boat['Class Dues'] = existing.get('Class Dues', 'Not Paid')
            # Preserve Yacht Club
            boat['Yacht Club'] = existing.get('Yacht Club', '')
            merged_count += 1
        else:
            # Initialize fields for new boats
            boat.setdefault('Yacht Club', '')
            boat['Fleet Dues'] = 'Not Paid'
            boat['Class Dues'] = 'Not Paid'
    
    logger.info(f"Merged preserved data for {merged_count} boats")
    return scraped_data

def load_fleet22_from_members():
    """Load Fleet 22 boats from j105_members_status.json, deduplicated by hull number."""
    if not MEMBERS_FILE.exists():
        logger.warning(f"Members file not found: {MEMBERS_FILE}")
        return None

    try:
        all_members = load_json(MEMBERS_FILE)
        fleet22_entries = [m for m in all_members if m.get('Fleet') == '22']
        logger.info(f"Found {len(fleet22_entries)} Fleet 22 entries in members data")

        # Deduplicate by hull number (multiple entries = co-owners)
        seen_hulls = set()
        boats = []
        for entry in fleet22_entries:
            hull = str(entry.get('Hull', ''))
            if hull and hull not in seen_hulls:
                seen_hulls.add(hull)
                boats.append({
                    'Hull Number': hull,
                    'Boat Name': entry.get('Boat Name', ''),
                })
        
        logger.info(f"Deduplicated to {len(boats)} unique Fleet 22 boats")
        return boats
    except Exception as e:
        logger.error(f"Error loading members data: {str(e)}")
        return None

def main():
    """Main execution function."""
    logger.info("Starting fleet boats builder")
    
    # Load existing data to preserve payment and yacht club information
    existing_data = get_existing_fleet_data()
    preserved_map = extract_preserved_data(existing_data)
    
    # Load Fleet 22 boats from members JSON
    fresh_data = load_fleet22_from_members()
    
    if fresh_data:
        # Merge fresh data with existing preserved data
        data = merge_preserved_data(fresh_data, preserved_map)
        logger.info("Updated boat list with preserved data")
    elif existing_data:
        # Use existing data if members file unavailable
        data = existing_data
        logger.info("Using existing boat data (members file unavailable)")
    else:
        logger.error("No data source available")
        print("Error: No data source available")
        return False
    
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