#!/usr/bin/env python3
"""
Payment status update script for Fleet22_us repository
Updates boats_fleet22.json with Class Dues payment status from membership data.
Fleet Dues are manually maintained in boats_fleet22.json.
"""
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import load_json, save_json
from utils.path_utils import (
    PROJECT_ROOT,
    BOATS_FILE,
    MEMBERS_FILE,
    PAYMENTS_DATA,
    ensure_directories
)

# Setup logging
logger = setup_logger('payment_sync', PROJECT_ROOT / 'logs' / 'data_management.log')

# Configuration
CURRENT_YEAR = datetime.now().year


def sync_class_dues_from_members(boats_data, members_data):
    """Sync Class Dues payment status from J/105 members data."""
    updated_count = 0
    
    try:
        # Extract hull numbers from boats for quick lookup
        boats_hull_numbers = {str(boat["Hull Number"]) for boat in boats_data}
        
        # Track latest membership status per hull
        latest_membership_status = {}
        
        for member in members_data:
            hull_number = str(member.get("Hull", ""))
            if hull_number in boats_hull_numbers:
                membership = member.get("Class Membership", "")
                membership_parts = membership.split()
                
                if membership_parts and membership_parts[-1].isdigit():
                    year = int(membership_parts[-1])
                    if hull_number not in latest_membership_status or year > latest_membership_status[hull_number]["year"]:
                        latest_membership_status[hull_number] = {
                            "year": year,
                            "status": membership
                        }
        
        # Update boats with Class Dues status
        for boat in boats_data:
            hull_number = str(boat.get("Hull Number", ""))
            member_info = latest_membership_status.get(hull_number)
            
            if member_info and member_info["year"] == CURRENT_YEAR:
                boat[f'Class Dues {CURRENT_YEAR}'] = 'Paid'
                boat['Class Dues Payment Date'] = f"{CURRENT_YEAR}-01-01"  # Approximate
                updated_count += 1
                logger.info(f"Hull {hull_number} ({boat.get('Boat Name', 'Unknown')}): Class Dues Paid for {CURRENT_YEAR}")
            else:
                boat[f'Class Dues {CURRENT_YEAR}'] = 'Unpaid'
                if member_info:
                    logger.info(f"Hull {hull_number}: Class Dues not paid for {CURRENT_YEAR} (last paid: {member_info['year']})")
        
        logger.info(f"Synced Class Dues for {updated_count} boats from members data")
        return boats_data, updated_count
        
    except Exception as e:
        logger.error(f"Error syncing Class Dues from members: {e}")
        return boats_data, 0


def generate_summary_report(boats_data):
    """Generate summary statistics for both Fleet and Class Dues."""
    total = len(boats_data)
    
    # Fleet Dues stats
    fleet_paid = sum(1 for b in boats_data if b.get(f'Fleet Dues {CURRENT_YEAR}') == 'Paid')
    fleet_unpaid = total - fleet_paid
    fleet_rate = (fleet_paid / total * 100) if total > 0 else 0
    
    # Class Dues stats  
    class_paid = sum(1 for b in boats_data if b.get(f'Class Dues {CURRENT_YEAR}') == 'Paid')
    class_unpaid = sum(1 for b in boats_data if b.get(f'Class Dues {CURRENT_YEAR}') == 'Unpaid')
    class_unknown = total - class_paid - class_unpaid
    class_rate = (class_paid / total * 100) if total > 0 else 0
    
    summary = f"""
{'='*80}
PAYMENT STATUS SYNC REPORT - {CURRENT_YEAR}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

FLEET DUES (Fleet 22 Dues)
--------------------------
Total Boats:       {total}
Paid:              {fleet_paid} ({fleet_rate:.1f}%)
Unpaid:            {fleet_unpaid} ({100-fleet_rate:.1f}%)
Outstanding:       ${fleet_unpaid * 150:,} (est. $150/boat)

CLASS DUES (J/105 Class Association)
------------------------------------
Total Boats:       {total}
Paid:              {class_paid} ({class_rate:.1f}%)
Unpaid:            {class_unpaid} ({100-class_rate:.1f}%)
Unknown:           {class_unknown}

DATA SOURCES
------------
✓ Fleet Dues: Manually maintained in boats_fleet22.json
✓ Class Dues: Synced from j105_members_status.json

NEXT STEPS
----------
1. Manually update Fleet Dues status in boats_fleet22.json as payments received
2. Re-run this script to sync Class Dues from membership data
3. Web pages will automatically show updated status
"""
    
    return summary, {
        'total': total,
        'fleet_paid': fleet_paid,
        'fleet_unpaid': fleet_unpaid,
        'class_paid': class_paid,
        'class_unpaid': class_unpaid,
        'class_unknown': class_unknown
    }


def main():
    """Main function to sync all payment status data."""
    try:
        logger.info("="*80)
        logger.info("Starting payment status synchronization...")
        logger.info("="*80)
        
        # Ensure directories exist
        ensure_directories()
        
        # Load boats data
        logger.info(f"Loading boats data from {BOATS_FILE}")
        boats_data = load_json(BOATS_FILE)
        if not boats_data:
            logger.error(f"Failed to load boats data from {BOATS_FILE}")
            print("❌ Error: Could not load boats data")
            return False
        
        logger.info(f"✓ Loaded {len(boats_data)} boats")
        print(f"Loaded {len(boats_data)} boats from boats_fleet22.json")
        
        # Fleet Dues are manually maintained in boats_fleet22.json
        print("\n� Fleet Dues: Manually maintained in boats_fleet22.json")
        logger.info("Fleet Dues status preserved from boats_fleet22.json (manual updates)")
        
        # Load members data for Class Dues
        logger.info(f"\nLoading members data from {MEMBERS_FILE}")
        members_data = load_json(MEMBERS_FILE)
        if members_data:
            logger.info(f"✓ Loaded {len(members_data)} member records")
            print(f"\n📊 Syncing Class Dues from J/105 members data...")
            boats_data, class_count = sync_class_dues_from_members(boats_data, members_data)
            print(f"✓ Updated Class Dues for {class_count} boats")
        else:
            logger.warning(f"Failed to load members data from {MEMBERS_FILE}")
            print("⚠️  Warning: Could not sync Class Dues (members data unavailable)")
        
        # Save updated boats data
        logger.info(f"\nSaving updated boats data to {BOATS_FILE}")
        save_json(boats_data, BOATS_FILE)
        logger.info("✓ Boats data saved with automatic backup")
        print(f"\n💾 Saved updated data to boats_fleet22.json (backup created)")
        
        # Generate and display summary
        summary, stats = generate_summary_report(boats_data)
        print(summary)
        logger.info(summary)
        
        # Save summary to file
        summary_path = PAYMENTS_DATA / f"payment_sync_summary_{CURRENT_YEAR}.txt"
        summary_path.write_text(summary)
        logger.info(f"Summary saved to {summary_path}")
        
        # Generate detailed report
        report_path = generate_detailed_report(boats_data, CURRENT_YEAR)
        logger.info(f"Detailed report saved to {report_path}")
        
        print(f"\n✅ Payment synchronization completed successfully!")
        print(f"📄 Summary: {summary_path}")
        print(f"📄 Report: {report_path}")
        print(f"\n💡 Tip: Manually update Fleet Dues in boats_fleet22.json as payments arrive")
        print(f"💡 Tip: Re-run this script weekly to sync Class Dues from membership data")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during payment synchronization: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False


def generate_detailed_report(boats_data, year):
    """Generate a detailed payment status report for both Fleet and Class Dues."""
    
    # Sort boats
    def get_hull_sort_key(boat):
        hull = boat.get('Hull Number', '')
        try:
            return int(hull)
        except (ValueError, TypeError):
            return 99999
    
    # Categorize by payment status
    fleet_paid = sorted([b for b in boats_data if b.get(f'Fleet Dues {year}') == 'Paid'], 
                        key=get_hull_sort_key)
    fleet_unpaid = sorted([b for b in boats_data if b.get(f'Fleet Dues {year}') != 'Paid'], 
                          key=get_hull_sort_key)
    
    class_paid = sorted([b for b in boats_data if b.get(f'Class Dues {year}') == 'Paid'], 
                        key=get_hull_sort_key)
    class_unpaid = sorted([b for b in boats_data if b.get(f'Class Dues {year}') == 'Unpaid'], 
                          key=get_hull_sort_key)
    
    # Build report
    report = f"{'='*80}\n"
    report += f"DETAILED PAYMENT STATUS REPORT - {year}\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"{'='*80}\n\n"
    
    # Fleet Dues Section
    report += f"FLEET DUES - PAID BOATS ({len(fleet_paid)})\n"
    report += "-" * 80 + "\n"
    for boat in fleet_paid:
        report += f"Hull {boat.get('Hull Number', ''):>4} | "
        report += f"{boat.get('Boat Name', 'Unknown'):<30} | "
        report += f"{boat.get('Yacht Club', ''):<10} | "
        report += f"Paid: {boat.get('Fleet Dues Payment Date', 'N/A')} "
        report += f"via {boat.get('Fleet Dues Payment Method', 'N/A')}\n"
    
    report += f"\nFLEET DUES - UNPAID BOATS ({len(fleet_unpaid)})\n"
    report += "-" * 80 + "\n"
    for boat in fleet_unpaid:
        report += f"Hull {boat.get('Hull Number', ''):>4} | "
        report += f"{boat.get('Boat Name', 'Unknown'):<30} | "
        report += f"{boat.get('Yacht Club', ''):<10} | "
        report += f"UNPAID\n"
    
    # Class Dues Section
    report += f"\n\nCLASS DUES - PAID BOATS ({len(class_paid)})\n"
    report += "-" * 80 + "\n"
    for boat in class_paid:
        report += f"Hull {boat.get('Hull Number', ''):>4} | "
        report += f"{boat.get('Boat Name', 'Unknown'):<30} | "
        report += f"{boat.get('Yacht Club', ''):<10} | "
        report += f"Paid for {year}\n"
    
    report += f"\nCLASS DUES - UNPAID BOATS ({len(class_unpaid)})\n"
    report += "-" * 80 + "\n"
    for boat in class_unpaid:
        report += f"Hull {boat.get('Hull Number', ''):>4} | "
        report += f"{boat.get('Boat Name', 'Unknown'):<30} | "
        report += f"{boat.get('Yacht Club', ''):<10} | "
        report += f"UNPAID\n"
    
    # Save the report
    report_path = PAYMENTS_DATA / f"payment_sync_report_{year}.txt"
    report_path.write_text(report)
    
    return report_path


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
