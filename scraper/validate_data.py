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

# Setup logging
logging.basicConfig(level=logging.INFO, filename='scraping.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
        
        # Check some expected fields in the first item
        expected_fields = ["Hull #", "Owner", "Class"]
        first_item = data[0]
        missing_fields = [field for field in expected_fields if field not in first_item]
        
        if missing_fields:
            logging.error(f"Missing fields in sail tags data: {missing_fields} - {filepath}")
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
        
        # Check some expected fields in the first item
        expected_fields = ["Hull #", "Owner", "Fleet", "Class Membership"]
        first_item = data[0]
        missing_fields = [field for field in expected_fields if field not in first_item]
        
        if missing_fields:
            logging.error(f"Missing fields in membership data: {missing_fields} - {filepath}")
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
            
        # Check some expected fields in the first item
        expected_fields = ["Hull #", "Owner", "Boat Name"]
        first_item = data[0]
        missing_fields = [field for field in expected_fields if field not in first_item]
        
        if missing_fields:
            logging.error(f"Missing fields in fleet boats data: {missing_fields} - {filepath}")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Error validating fleet boats data {filepath}: {str(e)}")
        return False

def run_validations():
    """Run all validations and return overall status."""
    data_dir = '../data'
    validation_status = True
    
    # Files to validate
    files_to_validate = {
        'sail_tags.json': validate_sail_tags_data,
        'j105_members_status.json': validate_membership_data,
        'boats_fleet22.json': validate_fleet_boats_data
    }
    
    for filename, validation_func in files_to_validate.items():
        filepath = os.path.join(data_dir, filename)
        
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