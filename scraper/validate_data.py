#!/usr/bin/env python3
"""
Data validation script for Fleet22_us repository
Checks the integrity and structure of scraped JSON data files.
"""
import json
import os
import sys
import logging
from datetime import datetime

# Setup logging to both file and console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("scraping.log", mode='a'),
                        logging.StreamHandler()
                    ])

def validate_file_exists(filepath):
    """Check if a file exists and is not empty."""
    if not os.path.exists(filepath):
        logging.error(f"File not found: {filepath}")
        return False
    
    if os.path.getsize(filepath) == 0:
        logging.error(f"File is empty: {filepath}")
        return False
    
    return True

def validate_json_format(filepath):
    """Check if a file contains valid JSON."""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {filepath}: {str(e)}")
        return False

def validate_sail_tags_data(filepath):
    """Validate the structure of sail_tags.json."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logging.error(f"Sail tags data should be a list: {filepath}")
            return False
        
        if len(data) == 0:
            logging.warning(f"Sail tags data is empty: {filepath}")
            return True  # Empty is valid, just suspicious
        
        # Print out the keys in the first item to help debug
        first_item = data[0]
        logging.info(f"First sail_tags.json item has keys: {list(first_item.keys())}")
        
        # Be more flexible with field names
        hull_fields = ["Hull", "Hull #", "Hull Number"]
        has_hull = any(field in first_item for field in hull_fields)
        
        owner_fields = ["Purchaser", "Owner", "Owners/Helmsmen"]
        has_owner = any(field in first_item for field in owner_fields)
        
        if not (has_hull and has_owner):
            logging.error(f"Missing required fields in sail tags data. Needs hull and owner information.")
            logging.error(f"Available fields: {list(first_item.keys())}")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Error validating sail tags data {filepath}: {str(e)}")
        return False

def validate_membership_data(filepath):
    """Validate the structure of j105_members_status.json."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logging.error(f"Membership data should be a list: {filepath}")
            return False
        
        if len(data) == 0:
            logging.warning(f"Membership data is empty: {filepath}")
            return True  # Empty is valid, just suspicious
        
        # Print out the keys in the first item to help debug
        first_item = data[0]
        logging.info(f"First j105_members_status.json item has keys: {list(first_item.keys())}")
        
        # Be more flexible with field names
        hull_fields = ["Hull", "Hull #", "Hull Number"]
        has_hull = any(field in first_item for field in hull_fields)
        
        owner_fields = ["Owner", "Owners/Helmsmen", "Owner Name"]
        has_owner = any(field in first_item for field in owner_fields)
        
        if not (has_hull and has_owner):
            logging.error(f"Missing required fields in membership data. Needs hull and owner information.")
            logging.error(f"Available fields: {list(first_item.keys())}")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Error validating membership data {filepath}: {str(e)}")
        return False

def validate_fleet_boats_data(filepath):
    """Validate the structure of boats_fleet22.json."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logging.error(f"Fleet boats data should be a list: {filepath}")
            return False
        
        if len(data) == 0:
            logging.warning(f"Fleet boats data is empty: {filepath}")
            return True  # Empty is valid, just suspicious
        
        # Print out the keys in the first item to help debug
        first_item = data[0]
        logging.info(f"First boats_fleet22.json item has keys: {list(first_item.keys())}")
        
        # Be more flexible with field names
        hull_fields = ["Hull", "Hull #", "Hull Number"]
        has_hull = any(field in first_item for field in hull_fields)
        
        boat_name_fields = ["Boat Name", "Name"]
        has_boat_name = any(field in first_item for field in boat_name_fields)
        
        if not (has_hull and has_boat_name):
            logging.error(f"Missing required fields in fleet boats data. Needs hull and boat name information.")
            logging.error(f"Available fields: {list(first_item.keys())}")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Error validating fleet boats data {filepath}: {str(e)}")
        return False

def run_validations():
    """Run all validations and return overall status."""
    # First try relative path for local development
    data_dir = '../data'
    if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
        # If not found, try current directory for GitHub Actions
        data_dir = 'data'
        if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
            logging.error(f"Data directory not found at '../data' or 'data'")
            return False
    
    logging.info(f"Using data directory: {data_dir}")
    validation_status = True
    
    # Files to validate
    files_to_validate = {
        'sail_tags.json': validate_sail_tags_data,
        'j105_members_status.json': validate_membership_data,
        'boats_fleet22.json': validate_fleet_boats_data
    }
    
    for filename, validation_func in files_to_validate.items():
        filepath = os.path.join(data_dir, filename)
        logging.info(f"Validating: {filepath}")
        
        # Check if file exists and is not empty
        if not validate_file_exists(filepath):
            validation_status = False
            continue
        
        # Check if file contains valid JSON
        if not validate_json_format(filepath):
            validation_status = False
            continue
        
        # Validate the structure of the data
        if not validation_func(filepath):
            validation_status = False
        else:
            logging.info(f"✅ {filename} passed validation.")
    
    if validation_status:
        logging.info("All data files are valid.")
        print("✅ All data files are valid.")
    else:
        logging.error("One or more data files are invalid.")
        print("❌ One or more data files are invalid. See logs for details.")
    
    return validation_status

if __name__ == "__main__":
    success = run_validations()
    sys.exit(0 if success else 1)