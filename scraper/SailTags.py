import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import os
from tqdm import tqdm

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

def fetch_url(url, headers):
    try:
        # Throttle requests to be polite to the server
        time.sleep(1)
        logging.info(f'Requesting {url}')
        # Disable SSL certificate verification
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        logging.error(f'HTTP error occurred: {e}')
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        logging.error(f'Request exception: {e}')
        raise SystemExit(e)

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    pollText_element = soup.find(class_='pollText')
    if pollText_element:
        return pollText_element.find_next('table')
    return None

def extract_table_data(table):
    headers_row = table.find('tr')
    headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
    if not headers:  # Fallback if headers are in 'td' tags
        headers = [clean_text(td.get_text()) for td in headers_row.find_all('td')]

    data_list = []
    for row in tqdm(table.find_all('tr')[1:], desc="Processing Rows"):
        cols = row.find_all('td')
        num_cols_to_process = min(len(cols), len(headers))
        row_data = {headers[i] if i < len(headers) else f"Unknown_{i}": clean_text(cols[i].text) for i in range(num_cols_to_process)}
        data_list.append(row_data)
    return data_list

def save_to_file(data, folder_path, file_name):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    json_file_path = os.path.join(folder_path, file_name)
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)
    logging.info(f'Data has been extracted and saved as {json_file_path}.')

# Main execution
html_content = fetch_url(url, headers)
table = parse_html(html_content)
if table:
    data = extract_table_data(table)
    save_to_file(data, '../data', 'sail_tags.json')
else:
    logging.warning('Table not found. The script may need adjustment based on the HTML structure.')
