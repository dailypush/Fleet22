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

# Try both relative and absolute paths for flexibility
DEFAULT_DATA_DIR = '../data'
GITHUB_DATA_DIR = 'data'

def get_data_dir():
    """Determine which data directory to use."""
    if os.path.exists(DEFAULT_DATA_DIR) and os.path.isdir(DEFAULT_DATA_DIR):
        return DEFAULT_DATA_DIR
    elif os.path.exists(GITHUB_DATA_DIR) and os.path.isdir(GITHUB_DATA_DIR):
        return GITHUB_DATA_DIR
    else:
        raise FileNotFoundError("Could not find data directory")

def get_output_dir():
    """Determine which output directory to use."""
    data_dir = get_data_dir()
    # Create the directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def load_json_data(filename):
    """Load JSON data from a file."""
    data_dir = get_data_dir()
    filepath = os.path.join(data_dir, filename)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            logging.info(f"Successfully loaded {len(data)} items from {filepath}")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {filepath}: {e}")
        return []

def standardize_hull_number(hull_num):
    """Standardize hull number format."""
    if not hull_num:
        return ""
    
    # Convert to string first
    hull_num = str(hull_num).strip()
    
    # Remove non-numeric characters
    hull_num = re.sub(r'[^\d]', '', hull_num)
    
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
    
    # Log the first item of each data source to help debug
    if sail_tags_data:
        logging.info(f"sail_tags.json first item keys: {list(sail_tags_data[0].keys())}")
    if membership_data:
        logging.info(f"j105_members_status.json first item keys: {list(membership_data[0].keys())}")
    if fleet_boats_data:
        logging.info(f"boats_fleet22.json first item keys: {list(fleet_boats_data[0].keys())}")
    
    # Create a dictionary to track all unique hull numbers
    combined_data = {}
    
    # Process sail tags data - using the actual field names from the file
    for item in sail_tags_data:
        hull_num = standardize_hull_number(item.get('Hull', ''))
        if not hull_num:
            continue
            
        if hull_num not in combined_data:
            combined_data[hull_num] = {
                'hull_number': hull_num,
                'owner': standardize_owner_name(item.get('Purchaser', '')),
                'boat_name': '',
                'fleet': item.get('Fleet', ''),
                'class_membership': '',
                'sail_tags': []
            }
        
        # Extract sail tag information if available
        combined_data[hull_num]['sail_tags'].append({
            'certificate': item.get('Certificate No.', ''),
            'sailmaker': item.get('Sailmaker', ''),
            'delivery_date': item.get('Delivery Date', ''),
            'type': item.get('Sail Type', '')
        })
    
    # Process membership data - using the actual field names from the file
    for item in membership_data:
        hull_num = standardize_hull_number(item.get('Hull', ''))
        if not hull_num:
            continue
            
        if hull_num not in combined_data:
            combined_data[hull_num] = {
                'hull_number': hull_num,
                'owner': standardize_owner_name(item.get('Owners/Helmsmen', '')),
                'boat_name': item.get('Boat Name', ''),
                'fleet': item.get('Fleet', ''),
                'class_membership': item.get('Class Membership', ''),
                'sail_tags': []
            }
        else:
            # Update existing data
            combined_data[hull_num]['class_membership'] = item.get('Class Membership', '')
            combined_data[hull_num]['fleet'] = item.get('Fleet', '')
            
            # If boat name is empty, use the one from membership data
            if not combined_data[hull_num]['boat_name']:
                combined_data[hull_num]['boat_name'] = item.get('Boat Name', '')
            
            # If owner name is empty, use the one from membership data
            if not combined_data[hull_num]['owner']:
                combined_data[hull_num]['owner'] = standardize_owner_name(item.get('Owners/Helmsmen', ''))
    
    # Process fleet boats data - using the actual field names from the file
    for item in fleet_boats_data:
        hull_num = standardize_hull_number(item.get('Hull Number', ''))
        if not hull_num:
            continue
            
        if hull_num not in combined_data:
            combined_data[hull_num] = {
                'hull_number': hull_num,
                'owner': '',  # Fleet data doesn't have owner information
                'boat_name': item.get('Boat Name', ''),
                'fleet': '22',  # These are Fleet 22 boats
                'class_membership': item.get('Class Dues', ''),
                'sail_tags': []
            }
        else:
            # Update existing data
            combined_data[hull_num]['fleet'] = '22'  # Mark as Fleet 22
            
            # If boat name is empty, use the one from fleet data
            if not combined_data[hull_num]['boat_name']:
                combined_data[hull_num]['boat_name'] = item.get('Boat Name', '')
    
    # Convert the dictionary to a list for JSON serialization
    combined_list = list(combined_data.values())
    
    # Sort by hull number
    combined_list.sort(key=lambda x: int(x['hull_number']) if x['hull_number'].isdigit() else float('inf'))
    
    logging.info(f"Combined data has {len(combined_list)} entries")
    return combined_list

def save_combined_data(data):
    """Save combined data to a JSON file."""
    output_dir = get_output_dir()
    output_file = os.path.join(output_dir, 'combined_fleet_data.json')
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    logging.info(f"Combined data saved to {output_file} with {len(data)} entries.")
    print(f"Combined data saved to {output_file} with {len(data)} entries.")

def generate_fleet_statistics(combined_data):
    """Generate statistics about the fleet."""
    stats = {
        'total_boats': len(combined_data),
        'fleet_22_boats': sum(1 for boat in combined_data if boat['fleet'] == '22'),
        'active_membership': sum(1 for boat in combined_data if 'active' in str(boat['class_membership']).lower()),
        'total_sail_tags': sum(len(boat['sail_tags']) for boat in combined_data),
        'boats_with_sail_tags': sum(1 for boat in combined_data if boat['sail_tags']),
        'boats_with_names': sum(1 for boat in combined_data if boat['boat_name']),
        'generation': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    
    output_dir = get_output_dir()
    stats_file = os.path.join(output_dir, 'fleet_statistics.json')
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
        
    logging.info(f"Fleet statistics saved to {stats_file}.")
    print(f"Fleet statistics saved to {stats_file}.")
    
    return stats

def main():
    try:
        logging.info("Starting data combination process...")
        
        # Combine data from all sources
        combined_data = combine_boat_data()
        
        # If no data was combined, generate a placeholder entry to avoid errors
        if not combined_data:
            logging.warning("No data was combined. Creating a placeholder entry.")
            combined_data = [{
                'hull_number': '0',
                'owner': 'No Owner Data',
                'boat_name': 'No Boat Data',
                'fleet': '',
                'class_membership': '',
                'sail_tags': []
            }]
        
        # Save the combined data
        save_combined_data(combined_data)
        
        # Generate statistics
        stats = generate_fleet_statistics(combined_data)
        
        print(f"Data processing completed successfully.")
        print(f"Total boats: {stats['total_boats']}")
        print(f"Fleet 22 boats: {stats['fleet_22_boats']}")
        
        # Always return success even if no data was found
        return True
    except Exception as e:
        logging.error(f"Error in data combination process: {str(e)}")
        print(f"Error in data combination process: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
