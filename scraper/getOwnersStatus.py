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



# URL of the website to scrape and headers to mimic a browser visit
url = 'https://archive.j105.org/members/owners.php'
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

# Specific CSS selector for the table, ensure it correctly points to the table you're interested in
selector = 'table[width="98%"]'
table = soup.select_one(selector)


if table:
    # Extract headers from the first row's <td> elements
    first_row = table.find('tr')
    if first_row:
        headers = [td.text.strip() for td in first_row.find_all('td')]
    
    # Initialize a list to hold all rows of data
    data_list = []
    
    # Iterate over each row in the table starting from the second row
    for row in tqdm(table.find_all('tr')[1:], desc="Scraping Rows"):
        cols = row.find_all('td')
        if len(cols) == len(headers):
            # Directly address the problematic field by index or header name if known
            # Example: Assuming "Class Membership" is the last column
            class_membership_text = cols[-1].text.replace('\n', ' ').strip()
            class_membership_text = re.sub(r'\s+', ' ', class_membership_text)
            
            # Apply general sanitization to other fields
            row_data = {headers[i]: re.sub(r'\s+', ' ', cols[i].text).strip() for i in range(len(cols)-1)}
            
            # Update the problematic field with sanitized text
            row_data["Class Membership"] = class_membership_text
            # Check if the 'Fleet' column matches '22'
            if row_data.get("Fleet") == "22":
                data_list.append(row_data)

        else:
            logging.warning(f'Skipping row with unexpected number of columns: {len(cols)} expected: {len(headers)}')
    
    # Convert the list to JSON and save
    json_data = json.dumps(data_list, indent=4)
    # Generate a filename with the current date
    # date_str = datetime.now().strftime("%Y-%m-%d")
    # filename = f"j105_members_status_{date_str}.json"
    # Ensure the 'data' folder exists
    folder_path = '../data'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Define the full path for the JSON output file
    json_file_path = os.path.join(folder_path, 'j105_members_status.json')

    # Use this filename when saving the JSON data
    with open(json_file_path, 'w') as file:
        file.write(json_data)

    logging.info(f'Data has been extracted and saved as {json_file_path}.')
else:
    logging.warning('Table not found. Check the CSS selector.')
