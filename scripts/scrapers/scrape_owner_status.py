import requests
from bs4 import BeautifulSoup
import time
import re
import sys
import html
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import load_json, save_json
from utils.http_client import fetch_text
from utils.validation import validate_update
from utils.path_utils import MEMBERS_FILE

# Setup logging
logger = setup_logger(__name__)

# URL of the website to scrape and headers to mimic a browser visit
URL = 'https://archive.j105.org/members/owners.php'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch_owner_status() -> str:
    """
    Fetch owner status data from J105 archive.
    
    Returns:
        The response text content
        
    Raises:
        requests.RequestException: If the request fails
    """
    try:
        # Throttle requests to be polite to the server
        time.sleep(1)
        
        # Send a GET request to the website with headers
        logger.info(f'Requesting {URL}')
        
        return fetch_text(URL, HEADERS)

    except requests.exceptions.RequestException as e:
        logger.error(f'Request failed: {e}')
        raise

def parse_owner_data(html_content: str) -> List[Dict[str, str]]:
    """
    Parse HTML content and extract owner data.
    
    Args:
        html_content: Raw HTML string
        
    Returns:
        List of dictionaries containing owner data
    """
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Specific CSS selector for the table
    selector = 'table[width="98%"]'
    table = soup.select_one(selector)

    if not table:
        logger.warning('Table not found. Check the CSS selector.')
        return []

    # Extract headers from the first row's <td> elements
    first_row = table.find('tr')
    if not first_row:
        logger.warning('No header row found in table.')
        return []
    
    headers = [td.text.strip() for td in first_row.find_all('td')]
    
    # Initialize a list to hold all rows of data
    data_list = []
    
    # Iterate over each row in the table starting from the second row
    rows = table.find_all('tr')[1:]
    for row in tqdm(rows, desc="Processing Rows"):
        cols = row.find_all('td')
        if len(cols) == len(headers):
            # Sanitize the Class Membership field (last column)
            class_membership_text = cols[-1].text.replace('\n', ' ').strip()
            class_membership_text = re.sub(r'\s+', ' ', class_membership_text)
            # Decode any HTML entities that might have been missed
            class_membership_text = html.unescape(class_membership_text)
            
            # Apply general sanitization to other fields
            row_data = {}
            for i in range(len(cols)-1):
                # Get text, sanitize whitespace, and decode HTML entities
                text = re.sub(r'\s+', ' ', cols[i].text).strip()
                text = html.unescape(text)
                row_data[headers[i]] = text
            
            # Update the Class Membership field with sanitized text
            row_data["Class Membership"] = class_membership_text
            data_list.append(row_data)
        else:
            logger.warning(f'Skipping row with unexpected number of columns: {len(cols)} expected: {len(headers)}')
    
    return data_list

def main():
    """Main execution function."""
    logger.info("Starting owner status scraper")
    
    try:
        # Fetch data from website
        html_content = fetch_owner_status()
        
        # Parse the HTML
        data_list = parse_owner_data(html_content)
        
        if data_list:
            previous = load_json(MEMBERS_FILE) if MEMBERS_FILE.exists() else None
            validate_update(data_list, previous, 'members')
            save_json(data_list, MEMBERS_FILE)
            logger.info(f"Successfully scraped {len(data_list)} owner records")
        else:
            raise ValueError("No owner records extracted; keeping the previous snapshot")
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
