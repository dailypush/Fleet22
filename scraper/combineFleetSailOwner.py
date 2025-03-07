#!/usr/bin/env python3
"""
Data unification script for Fleet22_us repository
Combines and harmonizes data from multiple sources into a consolidated dataset.
"""
import json
import os
import logging
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, filename='scraping.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

DATA_DIR = '../data'
OUTPUT_DIR = '../data'

def load_json_data(filename):
    """Load JSON data from a file."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {filepath}: {e}")
        return []

def standardize_hull_number(hull_num):
    """Standardize hull number format."""
    if not hull_num:
        return ""
    
    # Remove non-numeric characters
    hull_num = re.sub(r'[^\d]', '', str(hull_num))
    
    # Return as string, or empty string if invalid
    return hull_num if hull_num else ""

def standardize_owner_name(owner_name):
    """Standardize owner name format."""
    if not owner_name:
        return ""
    
    # Convert to string
    owner_name = str(owner_name).strip()
    
    # Remove extra spaces
    owner_name = re.sub(r'\s+', ' ', owner_name)
    
    return owner_name

def combine_boat_data():
    """Combine boat data from multiple sources."""
    sail_tags_data = load_json_data('sail_tags.json')
    membership_data = load_json_data('j105_members_status.json')
    fleet_boats_data = load_json_data('boats_fleet22.json')
    
    # Create a dictionary to track all unique hull numbers
    combined_data = {}
    
    # Process sail tags data
    for item in sail_tags_data:
        hull_num = standardize_hull_number(item.get('Hull #', ''))
        if not hull_num:
            continue
            
        if hull_num not in combined_data:
            combined_data[hull_num] = {
                'hull_number': hull_num,
                'owner': standardize_owner_name(item.get('Owner', '')),
                'boat_name': '',
                'fleet': '',
                'class_membership': '',
                'sail_tags': []
            }
        
        # Extract sail tag information if available
        if 'Sail Tag' in item:
            combined_data[hull_num]['sail_tags'].append({
                'tag': item.get('Sail Tag', ''),
                'type': item.get('Type', ''),
                'year': item.get('Year', '')
            })
    
    # Process membership data
    for item in membership_data:
        hull_num = standardize_hull_number(item.get('Hull #', ''))
        if not hull_num:
            continue
            
        if hull_num not in combined_data:
            combined_data[hull_num] = {
                'hull_number': hull_num,
                'owner': standardize_owner_name(item.get('Owner', '')),
                'boat_name': '',
                'fleet': '',
                'class_membership': '',
                'sail_tags': []
            }
        
        # Update with membership information
        combined_data[hull_num]['class_membership'] = item.get('Class Membership', '')
        combined_data[hull_num]['fleet'] = item.get('Fleet', '')
        
        # If owner name is empty, use the one from membership data
        if not combined_data[hull_num]['owner']:
            combined_data[hull_num]['owner'] = standardize_owner_name(item.get('Owner', ''))
    
    # Process fleet boats data
    for item in fleet_boats_data:
        hull_num = standardize_hull_number(item.get('Hull #', ''))
        if not hull_num:
            continue
            
        if hull_num not in combined_data:
            combined_data[hull_num] = {
                'hull_number': hull_num,
                'owner': standardize_owner_name(item.get('Owner', '')),
                'boat_name': '',
                'fleet': '22',  # Assuming these are all Fleet 22 boats
                'class_membership': '',
                'sail_tags': []
            }
        
        # Update with fleet-specific information
        combined_data[hull_num]['boat_name'] = item.get('Boat Name', '')
        
        # If owner name is empty, use the one from fleet data
        if not combined_data[hull_num]['owner']:
            combined_data[hull_num]['owner'] = standardize_owner_name(item.get('Owner', ''))
    
    # Convert the dictionary to a list for JSON serialization
    combined_list = list(combined_data.values())
    
    # Sort by hull number
    combined_list.sort(key=lambda x: int(x['hull_number']) if x['hull_number'].isdigit() else float('inf'))
    
    return combined_list

def save_combined_data(data):
    """Save combined data to a JSON file."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    output_file = os.path.join(OUTPUT_DIR, 'combined_fleet_data.json')
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    logging.info(f"Combined data saved to {output_file} with {len(data)} entries.")
    print(f"Combined data saved to {output_file} with {len(data)} entries.")

def generate_fleet_statistics(combined_data):
    """Generate statistics about the fleet."""
    stats = {
        'total_boats': len(combined_data),
        'fleet_22_boats': sum(1 for boat in combined_data if boat['fleet'] == '22'),
        'active_membership': sum(1 for boat in combined_data if 'active' in boat['class_membership'].lower()),
        'total_sail_tags': sum(len(boat['sail_tags']) for boat in combined_data),
        'boats_with_sail_tags': sum(1 for boat in combined_data if boat['sail_tags']),
        'boats_with_names': sum(1 for boat in combined_data if boat['boat_name']),
        'generation': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    
    stats_file = os.path.join(OUTPUT_DIR, 'fleet_statistics.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
        
    logging.info(f"Fleet statistics saved to {stats_file}.")
    print(f"Fleet statistics saved to {stats_file}.")
    
    return stats

def main():
    try:
        # Combine data from all sources
        combined_data = combine_boat_data()
        
        # Save the combined data
        save_combined_data(combined_data)
        
        # Generate statistics
        stats = generate_fleet_statistics(combined_data)
        
        print(f"Data processing completed successfully.")
        print(f"Total boats: {stats['total_boats']}")
        print(f"Fleet 22 boats: {stats['fleet_22_boats']}")
        
        return True
    except Exception as e:
        logging.error(f"Error in data combination process: {str(e)}")
        print(f"Error in data combination process: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
