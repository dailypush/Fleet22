#!/usr/bin/env python3
"""
Enhanced Boat Data Manager
Manages boats_fleet22.json with payment tracking fields.
Preserves payment data when updating boat information.
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import load_json, save_json
from utils.path_utils import BOATS_FILE, PROJECT_ROOT

# Setup logging
logger = setup_logger('boat_data_manager', PROJECT_ROOT / 'logs' / 'data_management.log')

# Standard boat data structure with payment fields
BOAT_SCHEMA = {
    "Hull Number": "",
    "Boat Name": "",
    "Yacht Club": "",
    "Owner": "",
    "Contact Email": "",
    "Fleet Dues 2025": "Unpaid",  # Paid/Unpaid
    "Fleet Dues Payment Date": "",
    "Fleet Dues Payment Method": "",
    "Class Dues 2025": "Unknown",  # Paid/Unpaid/Unknown
    "Class Dues Payment Date": "",
    "Notes": ""
}

def load_boats_data():
    """Load existing boats data."""
    try:
        if BOATS_FILE.exists():
            boats = load_json(BOATS_FILE)
            logger.info(f"Loaded {len(boats)} boats from {BOATS_FILE}")
            return boats
        else:
            logger.warning(f"Boats file not found: {BOATS_FILE}")
            return []
    except Exception as e:
        logger.error(f"Error loading boats data: {e}")
        raise

def enhance_boat_data(boats_data):
    """Add payment fields to boats that don't have them."""
    enhanced_count = 0
    
    for boat in boats_data:
        original_keys = set(boat.keys())
        
        # Add any missing fields from schema
        for field, default_value in BOAT_SCHEMA.items():
            if field not in boat:
                boat[field] = default_value
                enhanced_count += 1
        
        # Log if boat was enhanced
        if set(boat.keys()) != original_keys:
            logger.info(f"Enhanced boat {boat.get('Hull Number', 'Unknown')}: Added {set(boat.keys()) - original_keys}")
    
    return boats_data, enhanced_count

def update_boat_payment(boats_data, hull_number, dues_type, paid=True, payment_date=None, payment_method=None):
    """Update payment status for a specific boat."""
    boat_found = False
    
    for boat in boats_data:
        if str(boat.get('Hull Number', '')) == str(hull_number):
            boat_found = True
            
            if dues_type.lower() == 'fleet':
                boat['Fleet Dues 2025'] = 'Paid' if paid else 'Unpaid'
                if payment_date:
                    boat['Fleet Dues Payment Date'] = payment_date
                if payment_method:
                    boat['Fleet Dues Payment Method'] = payment_method
                logger.info(f"Updated Fleet Dues for hull {hull_number}: {boat['Fleet Dues 2025']}")
                
            elif dues_type.lower() == 'class':
                boat['Class Dues 2025'] = 'Paid' if paid else 'Unpaid'
                if payment_date:
                    boat['Class Dues Payment Date'] = payment_date
                logger.info(f"Updated Class Dues for hull {hull_number}: {boat['Class Dues 2025']}")
            
            break
    
    if not boat_found:
        logger.warning(f"Boat with hull {hull_number} not found")
        return False
    
    return True

def merge_with_tracker(boats_data, tracker_csv_path):
    """Merge payment data from payment tracker CSV."""
    import csv
    
    try:
        if not Path(tracker_csv_path).exists():
            logger.warning(f"Tracker CSV not found: {tracker_csv_path}")
            return boats_data, 0
        
        # Create a mapping of hull -> payment info
        payment_map = {}
        
        with open(tracker_csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                hull = row.get('Hull', '')
                if hull and row.get('Paid 2025', '').upper() == 'YES':
                    payment_map[hull] = {
                        'paid': True,
                        'date': row.get('Payment Date', ''),
                        'method': row.get('Payment Method', '')
                    }
        
        # Update boats data with payment info
        updated_count = 0
        for boat in boats_data:
            hull = str(boat.get('Hull Number', ''))
            if hull in payment_map:
                payment_info = payment_map[hull]
                boat['Fleet Dues 2025'] = 'Paid'
                boat['Fleet Dues Payment Date'] = payment_info['date']
                boat['Fleet Dues Payment Method'] = payment_info['method']
                updated_count += 1
                logger.info(f"Merged payment data for hull {hull}")
        
        logger.info(f"Merged payment data for {updated_count} boats from tracker")
        return boats_data, updated_count
        
    except Exception as e:
        logger.error(f"Error merging with tracker: {e}")
        raise

def generate_report(boats_data):
    """Generate payment status report."""
    total = len(boats_data)
    fleet_paid = sum(1 for b in boats_data if b.get('Fleet Dues 2025') == 'Paid')
    fleet_unpaid = sum(1 for b in boats_data if b.get('Fleet Dues 2025') == 'Unpaid')
    class_paid = sum(1 for b in boats_data if b.get('Class Dues 2025') == 'Paid')
    class_unpaid = sum(1 for b in boats_data if b.get('Class Dues 2025') == 'Unpaid')
    
    print("\n" + "=" * 80)
    print("BOATS DATA PAYMENT STATUS REPORT")
    print("=" * 80)
    print(f"Total Boats:           {total}")
    print(f"\nFleet Dues 2025:")
    print(f"  Paid:                {fleet_paid} ({fleet_paid/total*100:.1f}%)")
    print(f"  Unpaid:              {fleet_unpaid} ({fleet_unpaid/total*100:.1f}%)")
    print(f"\nClass Dues 2025:")
    print(f"  Paid:                {class_paid} ({class_paid/total*100:.1f}%)")
    print(f"  Unpaid:              {class_unpaid} ({class_unpaid/total*100:.1f}%)")
    print(f"  Unknown:             {total - class_paid - class_unpaid}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description="Manage boats_fleet22.json with payment tracking"
    )
    parser.add_argument(
        'action',
        choices=['enhance', 'update', 'merge', 'report'],
        help="Action to perform"
    )
    parser.add_argument(
        '--hull',
        type=str,
        help="Hull number (for update action)"
    )
    parser.add_argument(
        '--type',
        choices=['fleet', 'class'],
        help="Dues type: fleet or class (for update action)"
    )
    parser.add_argument(
        '--paid',
        action='store_true',
        help="Mark as paid (for update action)"
    )
    parser.add_argument(
        '--date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help="Payment date (YYYY-MM-DD)"
    )
    parser.add_argument(
        '--method',
        type=str,
        help="Payment method"
    )
    parser.add_argument(
        '--tracker',
        type=Path,
        default=PROJECT_ROOT / 'data' / 'payments' / 'payment_tracker_2025.csv',
        help="Path to payment tracker CSV (for merge action)"
    )
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting boat data management action: {args.action}")
        
        # Load boats data
        boats_data = load_boats_data()
        
        if not boats_data:
            print("❌ No boats data found")
            return 1
        
        if args.action == 'enhance':
            # Add payment fields to all boats
            enhanced_data, count = enhance_boat_data(boats_data)
            save_json(enhanced_data, BOATS_FILE)
            print(f"✅ Enhanced {len(enhanced_data)} boats")
            print(f"📝 Added {count} missing fields")
            generate_report(enhanced_data)
            
        elif args.action == 'update':
            if not args.hull or not args.type:
                print("❌ Error: --hull and --type required for update")
                return 1
            
            # Ensure boat has payment fields
            boats_data, _ = enhance_boat_data(boats_data)
            
            # Update payment status
            success = update_boat_payment(
                boats_data,
                args.hull,
                args.type,
                paid=args.paid,
                payment_date=args.date,
                payment_method=args.method
            )
            
            if success:
                save_json(boats_data, BOATS_FILE)
                print(f"✅ Updated {args.type} dues for hull {args.hull}")
                generate_report(boats_data)
            else:
                print(f"❌ Boat hull {args.hull} not found")
                return 1
                
        elif args.action == 'merge':
            # Merge payment data from tracker CSV
            boats_data, _ = enhance_boat_data(boats_data)
            merged_data, count = merge_with_tracker(boats_data, args.tracker)
            save_json(merged_data, BOATS_FILE)
            print(f"✅ Merged payment data from tracker")
            print(f"📝 Updated {count} boats")
            generate_report(merged_data)
            
        elif args.action == 'report':
            generate_report(boats_data)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during boat data management: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
