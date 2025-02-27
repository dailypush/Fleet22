import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, filename='../data/scraping.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load the JSON data for boats and members status
with open('../data/boats_fleet22.json', 'r') as file:
    boats_fleet22 = json.load(file)

# Extract hull numbers from boats_fleet22 to create a set of hull numbers for quick lookup
boats_fleet22_hull_numbers = {boat["Hull Number"] for boat in boats_fleet22}

with open('../data/j105_members_status.json', 'r') as file:
    members_status = json.load(file)

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
    if member_info and member_info["year"] == 2025:
        boat["Class Dues"] = "Paid"
        logging.info(f"Hull Number {hull_number} ({boat.get('Boat Name', 'Unknown')}) is marked as Paid for 2025.")
    elif member_info:
        logging.info(f"Hull Number {hull_number} ({boat.get('Boat Name', 'Unknown')}) has not paid for 2025, highest year paid: {member_info['year']}.")
        print(f"Hull Number {hull_number}({boat.get('Boat Name', 'Unknown')}) has not paid Class Dues for 2025, highest year paid: {member_info['year']}.")

# Save the updated boats list back to the original file
updated_boats_file_path = '../data/boats_fleet22.json'
with open(updated_boats_file_path, 'w') as file:
    json.dump(boats_fleet22, file, indent=4)

logging.info(f"Updated boats list with Class Dues status saved to {updated_boats_file_path}")
