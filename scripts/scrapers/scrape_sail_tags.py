import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import save_json
from utils.path_utils import SAILS_DATA

# Setup logging
logger = setup_logger(__name__)

def clean_text(text: str) -> str:
    """Clean text by removing non-breaking spaces and stripping whitespace."""
    return text.replace('\u00a0', ' ').strip()

# URL of the website to scrape and headers to mimic a browser visit
URL = 'https://archive.j105.org/members/sail_tag_list.php'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch_url(url: str, headers: Dict[str, str]) -> str:
    """
    Fetch content from a URL with error handling.
    
    Args:
        url: The URL to fetch
        headers: Request headers
        
    Returns:
        The response text content
        
    Raises:
        requests.RequestException: If the request fails
    """
    try:
        # Throttle requests to be polite to the server
        time.sleep(1)
        logger.info(f'Requesting {url}')
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f'Request failed: {e}')
        raise

def parse_html(html: str) -> Optional[Any]:
    """
    Parse HTML content to find the data table.
    
    Args:
        html: Raw HTML string
        
    Returns:
        BeautifulSoup Tag object for the table, or None if not found
    """
    soup = BeautifulSoup(html, 'html.parser')
    pollText_element = soup.find(class_='pollText')
    if pollText_element:
        return pollText_element.find_next('table')
    return None

def extract_table_data(table: Any) -> List[Dict[str, str]]:
    """
    Extract data from the HTML table.
    
    Args:
        table: BeautifulSoup Tag object for the table
        
    Returns:
        List of dictionaries containing row data
    """
    headers_row = table.find('tr')
    headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
    if not headers:  # Fallback if headers are in 'td' tags
        headers = [clean_text(td.get_text()) for td in headers_row.find_all('td')]

    data_list = []
    rows = table.find_all('tr')[1:]
    
    for row in tqdm(rows, desc="Processing Rows"):
        cols = row.find_all('td')
        if not cols:
            continue
            
        num_cols_to_process = min(len(cols), len(headers))
        row_data = {
            headers[i] if i < len(headers) else f"Unknown_{i}": clean_text(cols[i].text) 
            for i in range(num_cols_to_process)
        }
        data_list.append(row_data)
    return data_list

def main():
    """Main execution function."""
    logger.info("Starting sail tags scraper")
    
    try:
        html_content = fetch_url(URL, HEADERS)
        table = parse_html(html_content)
        
        if table:
            data = extract_table_data(table)
            if data:
                output_file = SAILS_DATA / 'sail_tags.json'
                save_json(data, output_file)
                logger.info(f"Successfully scraped {len(data)} sail tag records")
            else:
                logger.warning("No data extracted from table")
        else:
            logger.warning('Table not found. The script may need adjustment based on the HTML structure.')
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
