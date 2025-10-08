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
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.path_utils import (
    PROJECT_ROOT, 
    BOATS_FILE, 
    SAILS_FILE, 
    MEMBERS_FILE,
    ensure_directories
)

# Setup logging
logger = setup_logger('validator', PROJECT_ROOT / 'logs' / 'scraping.log')

def validate_file_exists(filepath):
    """Check if a file exists and is not empty."""
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return False
    
    if os.path.getsize(filepath) == 0:
        logger.error(f"File is empty: {filepath}")
        return False
    
    return True

def validate_json_format(filepath):
    """Check if a file contains valid JSON."""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {str(e)}")
        return False

def validate_sail_tags_data(filepath):
    """Validate the structure of sail_tags.json."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error(f"Sail tags data should be a list: {filepath}")
            return False
        
        if len(data) == 0:
            logger.warning(f"Sail tags data is empty: {filepath}")
            return True  # Empty is valid, just suspicious
        
        # Print out the keys in the first item to help debug
        first_item = data[0]
        logger.info(f"First sail_tags.json item has keys: {list(first_item.keys())}")
        
        # Be more flexible with field names
        hull_fields = ["Hull", "Hull #", "Hull Number"]
        has_hull = any(field in first_item for field in hull_fields)
        
        owner_fields = ["Purchaser", "Owner", "Owners/Helmsmen"]
        has_owner = any(field in first_item for field in owner_fields)
        
        if not (has_hull and has_owner):
            logger.error(f"Missing required fields in sail tags data. Needs hull and owner information.")
            logger.error(f"Available fields: {list(first_item.keys())}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating sail tags data {filepath}: {str(e)}")
        return False

def validate_membership_data(filepath):
    """Validate the structure of j105_members_status.json."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error(f"Membership data should be a list: {filepath}")
            return False
        
        if len(data) == 0:
            logger.warning(f"Membership data is empty: {filepath}")
            return True  # Empty is valid, just suspicious
        
        # Print out the keys in the first item to help debug
        first_item = data[0]
        logger.info(f"First j105_members_status.json item has keys: {list(first_item.keys())}")
        
        # Be more flexible with field names
        hull_fields = ["Hull", "Hull #", "Hull Number"]
        has_hull = any(field in first_item for field in hull_fields)
        
        owner_fields = ["Owner", "Owners/Helmsmen", "Owner Name"]
        has_owner = any(field in first_item for field in owner_fields)
        
        if not (has_hull and has_owner):
            logger.error(f"Missing required fields in membership data. Needs hull and owner information.")
            logger.error(f"Available fields: {list(first_item.keys())}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating membership data {filepath}: {str(e)}")
        return False

def validate_fleet_boats_data(filepath):
    """Validate the structure of boats_fleet22.json."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error(f"Fleet boats data should be a list: {filepath}")
            return False
        
        if len(data) == 0:
            logger.warning(f"Fleet boats data is empty: {filepath}")
            return True  # Empty is valid, just suspicious
        
        # Print out the keys in the first item to help debug
        first_item = data[0]
        logger.info(f"First boats_fleet22.json item has keys: {list(first_item.keys())}")
        
        # Be more flexible with field names
        hull_fields = ["Hull", "Hull #", "Hull Number"]
        has_hull = any(field in first_item for field in hull_fields)
        
        boat_name_fields = ["Boat Name", "Name"]
        has_boat_name = any(field in first_item for field in boat_name_fields)
        
        if not (has_hull and has_boat_name):
            logger.error(f"Missing required fields in fleet boats data. Needs hull and boat name information.")
            logger.error(f"Available fields: {list(first_item.keys())}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating fleet boats data {filepath}: {str(e)}")
        return False

def run_validations():
    """Run all validations and return overall status."""
    logger.info("Starting data validation...")
    
    # Ensure directories exist
    ensure_directories()
    
    validation_status = True
    
    # Files to validate with their new paths
    files_to_validate = {
        'sail_tags.json': (SAILS_FILE, validate_sail_tags_data),
        'j105_members_status.json': (MEMBERS_FILE, validate_membership_data),
        'boats_fleet22.json': (BOATS_FILE, validate_fleet_boats_data)
    }
    
    for filename, (filepath, validation_func) in files_to_validate.items():
        logger.info(f"Validating: {filepath}")
        
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
            logger.info(f"✅ {filename} passed validation.")
    
    if validation_status:
        logger.info("All data files are valid.")
        print("✅ All data files are valid.")
    else:
        logger.error("One or more data files are invalid.")
        print("❌ One or more data files are invalid. See logs for details.")
    
    return validation_status

if __name__ == "__main__":
    success = run_validations()
    sys.exit(0 if success else 1)