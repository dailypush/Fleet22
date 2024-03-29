import requests
from bs4 import BeautifulSoup
import json
import logging
import time

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
    # Initialize a list to hold all rows of data
    data_list = []

    # Extract table headers
    headers = [header.text.strip() for header in table.find_all('th')]

# Ensure headers list is defined before this part, and you have the correct number of headers
for row in table.find_all('tr')[1:]:  # Assuming the first row contains headers
    cols = row.find_all('td')
    if len(cols) == len(headers):  # Check if the row has the same number of columns as the headers
        row_data = {headers[i]: col.text.strip() for i, col in enumerate(cols)}
        data_list.append(row_data)
    else:
        logging.warning(f"Skipping row with unexpected number of columns: {len(cols)} expected: {len(headers)}")


    # Convert the list to JSON
    json_data = json.dumps(data_list, indent=4)

    # Save the JSON data to a file
    with open('data.json', 'w') as file:
        file.write(json_data)

    logging.info('Data has been extracted and saved as JSON.')
else:
    logging.warning('Table not found. Check the CSS selector.')

