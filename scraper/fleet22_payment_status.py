import json
# Load the JSON data for boats and members status
with open('../data/boats_fleet22.json', 'r') as file:
    boats_fleet22 = json.load(file)

with open('../data/j105_members_status.json', 'r') as file:
    members_status = json.load(file)

# Convert members status to a dictionary for faster lookups, using Hull Number as key
members_status_dict = {member["Hull"]: member for member in members_status}

# List to hold members not updated to 2024
not_updated_to_2024 = []

# Check each boat in fleet 22 against member status
for boat in boats_fleet22:
    hull_number = boat["Hull Number"]
    # Check if the boat's hull number is in members status and if its class membership is not updated to 2024
    if hull_number in members_status_dict:
        if "2024" not in members_status_dict[hull_number]["Class Membership"]:
            not_updated_to_2024.append(boat)

# Output the results
not_updated_to_2024_json = json.dumps(not_updated_to_2024, indent=4)
print(not_updated_to_2024_json)
