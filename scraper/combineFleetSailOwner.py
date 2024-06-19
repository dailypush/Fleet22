import json

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def combine_and_clean_data(boats_file, sail_tags_file, members_status_file, output_file):
    boats_fleet22 = load_json(boats_file)
    sail_tags = load_json(sail_tags_file)
    j105_members_status = load_json(members_status_file)

    # Prepare sail_tags by hull for easy lookup
    sail_tags_by_hull_list = {}
    for entry in sail_tags:
        hull = entry["Hull"]
        if hull not in sail_tags_by_hull_list:
            sail_tags_by_hull_list[hull] = []
        sail_tags_by_hull_list[hull].append(entry)

    # Prepare j105_members by hull for easy lookup, accounting for multiple entries
    j105_members_by_hull_list = {}
    for entry in j105_members_status:
        hull = entry["Hull"]
        if hull not in j105_members_by_hull_list:
            j105_members_by_hull_list[hull] = []
        j105_members_by_hull_list[hull].append(entry)

    # Combine data
    for boat in boats_fleet22:
        hull_number = boat["Hull Number"]

        # Include sail tags as a child node
        boat["sail_tags"] = sail_tags_by_hull_list.get(hull_number, [])

        # Include j105 members information if available, allowing for multiple entries
        boat["j105_members"] = j105_members_by_hull_list.get(hull_number, [])

    save_json(boats_fleet22, output_file)

# Example usage
boats_file = 'path/to/boats_fleet22.json'
sail_tags_file = 'path/to/sail_tags.json'
members_status_file = 'path/to/j105_members_status.json'
output_file = 'path/to/cleaned_boats_fleet22.json'

combine_and_clean_data(boats_file, sail_tags_file, members_status_file, output_file)
