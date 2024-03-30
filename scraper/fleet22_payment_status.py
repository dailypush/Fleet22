import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, filename='../data/scraping.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load the JSON data for boats and members status
with open('../data/boats_fleet22.json', 'r') as file:
    boats_fleet22 = json.load(file)

with open('../data/j105_members_status.json', 'r') as file:
    members_status = json.load(file)

# Initialize a dictionary to track the highest membership year for each hull
highest_membership_year = {}

# Populate the dictionary with the highest membership year found for each hull
for member in members_status:
    hull_number = member["Hull"]
    parts = member["Class Membership"].split()
    if parts and parts[-1].isdigit():  # Check if there is a year and it is numeric
        year = parts[-1]
        if hull_number in highest_membership_year:
            if year > highest_membership_year[hull_number]:
                highest_membership_year[hull_number] = year
        else:
            highest_membership_year[hull_number] = year
    else:
        logging.warning(f"Invalid or missing year in Class Membership for hull {hull_number}: '{member['Class Membership']}'")

# Update the "Class Dues" status in boats_fleet22 based on highest_membership_year
for boat in boats_fleet22:
    hull_number = boat["Hull Number"]
    boat_name = boat.get("Boat Name", "Unknown")  # Use a default value if "Boat Name" is missing
    # Default status to "Not Paid"
    boat["Class Dues"] = "Not Paid"
    if hull_number in highest_membership_year and highest_membership_year[hull_number] == "2024":
        boat["Class Dues"] = "Paid"
        logging.info(f"Hull Number {hull_number} ({boat_name}) is marked as Paid for 2024.")
    elif hull_number in highest_membership_year:
        logging.info(f"Hull Number {hull_number} ({boat_name}) has not paid for 2024, highest year paid: {highest_membership_year[hull_number]}.")

# Save the updated boats list back to the original file
updated_boats_file_path = '../data/boats_fleet22.json'
with open(updated_boats_file_path, 'w') as file:
    json.dump(boats_fleet22, file, indent=4)

logging.info(f"Updated boats list with Class Dues status saved to {updated_boats_file_path}")
