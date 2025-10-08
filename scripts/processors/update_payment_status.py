#!/usr/bin/env python3
"""
Payment status update script for Fleet22_us repository
Updates boat payment status based on membership data.
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
logger = setup_logger('payment_processor', PROJECT_ROOT / 'logs' / 'scraping.log')

# Configuration
CONFIG = {
    "current_year": datetime.now().year,
    "create_backup": True,  # Automatic backups via data_loader
}

def main():
    """Main function to update payment status."""
    try:
        logger.info("Starting payment status update...")
        
        # Ensure directories exist
        ensure_directories()
        
        # Load the JSON data for boats and members status
        boats_fleet22 = load_json(BOATS_FILE)
        if not boats_fleet22:
            logger.error(f"Failed to load boats data from {BOATS_FILE}")
            return False
        
        logger.info(f"Successfully loaded {len(boats_fleet22)} boats from {BOATS_FILE}")
        
        members_status = load_json(MEMBERS_FILE)
        if not members_status:
            logger.error(f"Failed to load members data from {MEMBERS_FILE}")
            return False
            
        logger.info(f"Successfully loaded {len(members_status)} member entries from {MEMBERS_FILE}")
        
        # Extract hull numbers from boats_fleet22 to create a set of hull numbers for quick lookup
        boats_fleet22_hull_numbers = {boat["Hull Number"] for boat in boats_fleet22}
        
        # Prepare a dictionary to hold the latest membership status for each hull
        latest_membership_status = {}

        for member in members_status:
            hull_number = member["Hull"]
            if hull_number in boats_fleet22_hull_numbers:
                membership_parts = member["Class Membership"].split()
                if membership_parts and membership_parts[-1].isdigit():
                    year = int(membership_parts[-1])
                    if hull_number not in latest_membership_status or year > latest_membership_status[hull_number]["year"]:
                        latest_membership_status[hull_number] = {"year": year, "status": member["Class Membership"]}

        # Now iterate through boats in boats_fleet22, updating "Class Dues" based on the latest membership status
        for boat in boats_fleet22:
            hull_number = boat["Hull Number"]
            member_info = latest_membership_status.get(hull_number)

            boat["Class Dues"] = "Not Paid"  # Default to "Not Paid"
            if member_info and member_info["year"] == CONFIG["current_year"]:
                boat["Class Dues"] = "Paid"
                logger.info(f"Hull Number {hull_number} ({boat.get('Boat Name', 'Unknown')}) is marked as Paid for {CONFIG['current_year']}.")
            elif member_info:
                logger.info(f"Hull Number {hull_number} ({boat.get('Boat Name', 'Unknown')}) has not paid for {CONFIG['current_year']}, highest year paid: {member_info['year']}.")
                print(f"Hull Number {hull_number}({boat.get('Boat Name', 'Unknown')}) has not paid Class Dues for {CONFIG['current_year']}, highest year paid: {member_info['year']}.")

        # Save the updated boats list (automatic backup via save_json)
        save_json(boats_fleet22, BOATS_FILE)
        logger.info(f"Updated boats list with Class Dues status saved to {BOATS_FILE}")

        # Generate and log summary statistics
        total_boats = len(boats_fleet22)
        paid_boats = sum(1 for boat in boats_fleet22 if boat.get("Class Dues") == "Paid")
        unpaid_boats = total_boats - paid_boats
        payment_rate = (paid_boats / total_boats) * 100 if total_boats > 0 else 0

        summary = f"""
----- Payment Status Summary for {CONFIG['current_year']} -----
Total boats: {total_boats}
Paid boats: {paid_boats} ({payment_rate:.1f}%)
Unpaid boats: {unpaid_boats} ({100-payment_rate:.1f}%)
        """

        print(summary)
        logger.info(summary)

        # Save summary to file in payments directory
        summary_path = PAYMENTS_DATA / f"payment_summary_{CONFIG['current_year']}.txt"
        summary_path.write_text(summary)
        logger.info(f"Payment summary saved to {summary_path}")

        # Generate and save detailed report
        report_path = generate_detailed_report(boats_fleet22, CONFIG['current_year'])
        logger.info(f"Detailed report saved to {report_path}")
        
        print(f"\n✅ Payment status update completed successfully!")
        print(f"Summary: {summary_path}")
        print(f"Report: {report_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(f"❌ Error updating payment status: {str(e)}")
        return False


def generate_detailed_report(boats_data, year):
    """Generate a detailed payment status report."""
    # Sort boats by payment status and then by hull number
    paid_boats = sorted([b for b in boats_data if b.get("Class Dues") == "Paid"], 
                        key=lambda x: x.get("Hull Number", ""))
    unpaid_boats = sorted([b for b in boats_data if b.get("Class Dues") != "Paid"], 
                          key=lambda x: x.get("Hull Number", ""))
    
    report = f"PAYMENT STATUS REPORT - {year}\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    report += "PAID BOATS\n"
    report += "----------\n"
    for boat in paid_boats:
        report += f"Hull: {boat.get('Hull Number', 'Unknown')} | "
        report += f"Boat: {boat.get('Boat Name', 'Unknown')} | "
        report += f"Owner: {boat.get('Owner', 'Unknown')}\n"
    
    report += "\nUNPAID BOATS\n"
    report += "------------\n"
    for boat in unpaid_boats:
        report += f"Hull: {boat.get('Hull Number', 'Unknown')} | "
        report += f"Boat: {boat.get('Boat Name', 'Unknown')} | "
        report += f"Owner: {boat.get('Owner', 'Unknown')}\n"
    
    # Save the report
    report_path = PAYMENTS_DATA / f"payment_report_{year}.txt"
    report_path.write_text(report)
    
    return report_path


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
