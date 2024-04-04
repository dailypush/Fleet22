import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import re
import os
from tqdm import tqdm
# from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, filename='scraping.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    return text.replace('\u00a0', ' ').strip()

# URL of the website to scrape and headers to mimic a browser visit
url = 'https://archive.j105.org/members/sail_tag_list.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

try:
    # Throttle requests to be polite to the server
    time.sleep(1)
    
    # Send a GET request to the website with headers
    logging.info(f'Requesting {url}')
    response = requests.get(url, headers=headers)
    response.raise_for_status()

except requests.exceptions.HTTPError as e:
    logging.error(f'HTTP error occurred: {e}')
    raise SystemExit(e)
except requests.exceptions.RequestException as e:
    logging.error(f'Request exception: {e}')
    raise SystemExit(e)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')
# Find the table by navigating from a known point
pollText_element = soup.find(class_='pollText')
table = None
if pollText_element:
    table = pollText_element.find_next('table')

if table:
    headers_row = table.find('tr')
    headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
    if not headers:  # Fallback if headers are in 'td' tags
        headers = [clean_text(td.get_text()) for td in headers_row.find_all('td')]

    data_list = []
    
# Using tqdm to show progress
for row in tqdm(table.find_all('tr')[1:], desc="Processing Rows"):
    cols = row.find_all('td')
    # Ensure we only iterate up to the number of headers to avoid index errors
    num_cols_to_process = min(len(cols), len(headers))
    
    # Construct row_data with error checking
    row_data = {}
    for i in range(num_cols_to_process):
        header = headers[i] if i < len(headers) else f"Unknown_{i}"
        row_data[header] = clean_text(cols[i].text) if i < len(cols) else ""
    
    # Append each row's data to data_list inside the loop
    data_list.append(row_data)


    json_data = json.dumps(data_list, indent=4)
    folder_path = '../data'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    json_file_path = os.path.join(folder_path, 'sail_tags.json')

    with open(json_file_path, 'w') as file:
        file.write(json_data)

    logging.info(f'Data has been extracted and saved as {json_file_path}.')
else:
    logging.warning('Table not found. The script may need adjustment based on the HTML structure.')