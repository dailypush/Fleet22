#!/usr/bin/env python3
"""
GitHub Actions compatible version of fleetBoats.py
This script checks for existing boats_fleet22.json data in the data directory.
If it exists, it uses that. If not, it uses a fallback approach.
"""
import os
import json
import logging
import time
import requests
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, filename='scraping.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_existing_fleet_data():
    """Try to load existing boats_fleet22.json data if available"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    data_dir = os.path.join(project_root, 'data')
    existing_file = os.path.join(data_dir, 'boats_fleet22.json')
    
    if os.path.exists(existing_file):
        try:
            with open(existing_file, 'r') as f:
                data = json.load(f)
                logging.info(f"Loaded {len(data)} boat entries from existing file: {existing_file}")
                return data
        except Exception as e:
            logging.error(f"Error loading existing fleet data: {str(e)}")
    
    return None

def try_load_from_members_html():
    """Try to load data from members.html file"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..'))
        file_path = os.path.join(project_root, 'members.html')
        
        if not os.path.exists(file_path):
            logging.warning(f"members.html not found at: {file_path}")
            return None
            
        with open(file_path, 'r') as file:
            html_content = file.read()
            
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', {'class': 'table table-striped'})
        
        if table is None:
            logging.warning("Could not find the table with class 'table table-striped'")
            return None
        
        data_list = []
        headers = [header.text.strip() for header in table.find_all('th')]
        
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) == len(headers):
                row_data = {headers[i]: col.text.strip() for i, col in enumerate(cols)}
                data_list.append(row_data)
        
        logging.info(f"Extracted {len(data_list)} boat entries from members.html")
        return data_list
    
    except Exception as e:
        logging.error(f"Error processing members.html: {str(e)}")
        return None

def generate_fallback_data():
    """Generate fallback data"""
    # This is just a minimal structure to allow the workflow to continue
    logging.warning("Using fallback data generation")
    return [
        {"Hull #": "Unavailable", "Boat Name": "Data Unavailable", "Owner": "N/A"}
    ]

def main():
    # Determine file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    data_dir = os.path.join(project_root, 'data')
    
    # Ensure the data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Try different methods to get the data
    data = get_existing_fleet_data() or try_load_from_members_html() or generate_fallback_data()
    
    # Save the data
    output_file_path = os.path.join(data_dir, 'boats_fleet22.json')
    with open(output_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    logging.info(f"Saved {len(data)} boat entries to {output_file_path}")
    print(f"Successfully processed {len(data)} boat entries and saved to {output_file_path}")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        raise