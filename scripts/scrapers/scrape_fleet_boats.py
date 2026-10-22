#!/usr/bin/env python3
"""
Fleet 22 boat data builder.
Loads Fleet 22 boats from j105_members_status.json (filtering by Fleet == "22"),
merges with existing boats_fleet22.json to preserve payment and yacht club data.
"""
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import load_json, save_json
from utils.path_utils import BOATS_FILE, MEMBERS_FILE
from utils.membership import best_membership, is_paid_membership, members_by_hull, primary_member
from utils.validation import validate_records, validate_update

# Setup logging
logger = setup_logger(__name__)

# Fields to preserve from existing data (manually maintained)
PRESERVE_FIELDS = [
    'Fleet Dues',
    'Yacht Club'
]

CURRENT_YEAR = str(date.today().year)

def get_existing_fleet_data():
    """Try to load existing boats_fleet22.json data if available"""
    if not BOATS_FILE.exists():
        raise FileNotFoundError("Existing boats file is required to preserve manual Fleet Dues")
    data = load_json(BOATS_FILE)
    validate_records(data, 'boats')
    return data


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
    """Merge scraped boat data with existing fleet dues and yacht club information.
    
    Class Dues are derived from the members JSON Class Membership field.
    Fleet Dues are manually maintained — only preserved from existing data.
    """
    merged_count = 0
    for boat in scraped_data:
        hull = str(boat.get('Hull Number', ''))
        if hull in preserved_map:
            existing = preserved_map[hull]
            # Preserve Fleet Dues (manually maintained — never overwrite)
            boat['Fleet Dues'] = existing.get('Fleet Dues', 'Not Paid')
            # Preserve Yacht Club
            boat['Yacht Club'] = existing.get('Yacht Club', '')
            merged_count += 1
        else:
            # Initialize fields for new boats
            boat.setdefault('Yacht Club', '')
            boat['Fleet Dues'] = 'Not Paid'

        # Class Dues derived from members data Class Membership field
        class_membership = boat.pop('Class Membership', '')
        boat['Class Dues'] = 'Paid' if is_paid_membership(class_membership, CURRENT_YEAR) else 'Not Paid'
    
    logger.info(f"Merged preserved data for {merged_count} boats")
    return scraped_data

def load_fleet22_from_members():
    """Load Fleet 22 boats from j105_members_status.json, deduplicated by hull number."""
    all_members = load_json(MEMBERS_FILE)
    validate_records(all_members, 'members')
    boats = []
    for hull, records in members_by_hull(all_members).items():
        fleet_records = [r for r in records if r['Fleet'] == '22']
        if not fleet_records:
            continue
        entry = primary_member(fleet_records, CURRENT_YEAR)
        boats.append({
            'Hull Number': hull,
            'Boat Name': entry.get('Boat Name', ''),
            'Class Membership': best_membership(records, CURRENT_YEAR),
        })
    if not boats:
        raise ValueError("No Fleet 22 boats extracted from members data")
    return sorted(boats, key=lambda boat: int(boat['Hull Number']))


def main():
    """Main execution function."""
    logger.info("Starting fleet boats builder")
    
    # Load existing data to preserve payment and yacht club information
    existing_data = get_existing_fleet_data()
    preserved_map = extract_preserved_data(existing_data)
    
    # Load Fleet 22 boats from members JSON
    fresh_data = load_fleet22_from_members()
    
    data = merge_preserved_data(fresh_data, preserved_map)
    validate_update(data, existing_data, 'boats')
    # Removed boats with paid dues require a deliberate roster update.
    new_hulls = {b['Hull Number'] for b in data}
    removed_paid = [b['Hull Number'] for b in existing_data
                    if b['Fleet Dues'] == 'Paid' and b['Hull Number'] not in new_hulls]
    if removed_paid:
        raise ValueError(f"Refusing to remove boats with manual paid dues: {removed_paid}")

    # Save the data
    save_json(data, BOATS_FILE)
    logger.info(f"Successfully processed {len(data)} boat entries")
    paid_count = len([b for b in data if b.get('Fleet Dues') == 'Paid'])
    print(f"Successfully processed {len(data)} boat entries and saved to {BOATS_FILE}")
    print(f"Preserved payment data: {paid_count} paid boats")
    
    return True

if __name__ == "__main__":
    try:
        sys.exit(0 if main() else 1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        raise
