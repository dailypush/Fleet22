import json
import logging
import os
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, filename='../data/scraping.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
CONFIG = {
    "current_year": datetime.now().year,  # Automatically get current year
    "boats_file_path": '../data/boats_fleet22.json',
    "members_file_path": '../data/j105_members_status.json',
    "output_file_path": '../data/boats_fleet22.json',
    "backup_file_path": '../data/boats_fleet22_backup_{timestamp}.json',
    "create_backup": True  # Whether to create a backup of the original file
}

try:
    # Check if files exist before attempting to open them
    boats_file_path = CONFIG["boats_file_path"]
    members_file_path = CONFIG["members_file_path"]
    
    if not os.path.exists(boats_file_path):
        raise FileNotFoundError(f"Boats data file not found: {boats_file_path}")
    
    if not os.path.exists(members_file_path):
        raise FileNotFoundError(f"Members status file not found: {members_file_path}")
    
    # Load the JSON data for boats and members status
    with open(boats_file_path, 'r') as file:
        try:
            boats_fleet22 = json.load(file)
            logging.info(f"Successfully loaded {len(boats_fleet22)} boats from {boats_file_path}")
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON format in {boats_file_path}")
            sys.exit(1)
    
    # Extract hull numbers from boats_fleet22 to create a set of hull numbers for quick lookup
    boats_fleet22_hull_numbers = {boat["Hull Number"] for boat in boats_fleet22}
    
    with open(members_file_path, 'r') as file:
        try:
            members_status = json.load(file)
            logging.info(f"Successfully loaded {len(members_status)} member entries from {members_file_path}")
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON format in {members_file_path}")
            sys.exit(1)

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
            logging.info(f"Hull Number {hull_number} ({boat.get('Boat Name', 'Unknown')}) is marked as Paid for {CONFIG['current_year']}.")
        elif member_info:
            logging.info(f"Hull Number {hull_number} ({boat.get('Boat Name', 'Unknown')}) has not paid for {CONFIG['current_year']}, highest year paid: {member_info['year']}.")
            print(f"Hull Number {hull_number}({boat.get('Boat Name', 'Unknown')}) has not paid Class Dues for {CONFIG['current_year']}, highest year paid: {member_info['year']}.")

    # Save the updated boats list back to the original file
    updated_boats_file_path = CONFIG["output_file_path"]
    with open(updated_boats_file_path, 'w') as file:
        json.dump(boats_fleet22, file, indent=4)

    logging.info(f"Updated boats list with Class Dues status saved to {updated_boats_file_path}")

    # Add at the end of your script

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
    logging.info(summary)

    # You could also save this to a separate summary file if needed
    with open(f"../data/payment_summary_{CONFIG['current_year']}.txt", 'w') as summary_file:
        summary_file.write(summary)

    def generate_detailed_report(boats_data):
        # Sort boats by payment status and then by hull number
        paid_boats = sorted([b for b in boats_data if b.get("Class Dues") == "Paid"], 
                            key=lambda x: x.get("Hull Number", ""))
        unpaid_boats = sorted([b for b in boats_data if b.get("Class Dues") != "Paid"], 
                              key=lambda x: x.get("Hull Number", ""))
        
        report = f"PAYMENT STATUS REPORT - {CONFIG['current_year']}\n"
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
        report_path = f"../data/payment_report_{CONFIG['current_year']}.txt"
        with open(report_path, 'w') as report_file:
            report_file.write(report)
        
        logging.info(f"Detailed report saved to {report_path}")
        return report_path

    # Generate the detailed report
    report_path = generate_detailed_report(boats_fleet22)

except Exception as e:
    logging.error(f"An error occurred: {str(e)}")
    sys.exit(1)
