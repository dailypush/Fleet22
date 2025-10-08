import os
from bs4 import BeautifulSoup
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, filename='logs/scraping.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Determine file paths in a more robust way
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
file_path = os.path.join(project_root, 'members.html')
data_dir = os.path.join(project_root, 'data')

# Ensure the data directory exists
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

try:
    # Log attempt to read the file
    logging.info(f"Attempting to read file: {file_path}")
    
    # Load the HTML content from the file
    with open(file_path, 'r') as file:
        html_content = file.read()
        
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table by class name
    table = soup.find('table', {'class': 'table table-striped'})
    
    if table is None:
        raise ValueError("Could not find the table with class 'table table-striped'")
    
    # Extract data
    data_list = []
    
    # Assuming the first row of the table is headers
    headers = [header.text.strip() for header in table.find_all('th')]
    
    # Process each row of the table
    for row in table.find_all('tr')[1:]:  # skip the header row
        cols = row.find_all('td')
        if len(cols) == len(headers):  # Make sure the row has the expected number of columns
            row_data = {headers[i]: col.text.strip() for i, col in enumerate(cols)}
            data_list.append(row_data)
    
    # Convert the list to JSON
    json_output = json.dumps(data_list, indent=4)
    
    # Specify the JSON output file path
    output_file_path = os.path.join(data_dir, 'boats_fleet22.json')
    
    # Write the JSON data to a file
    with open(output_file_path, 'w') as json_file:
        json_file.write(json_output)
    
    logging.info(f"Successfully processed {len(data_list)} boat entries and saved to {output_file_path}")
    print(f"Successfully processed {len(data_list)} boat entries and saved to {output_file_path}")
    
except Exception as e:
    logging.error(f"Error processing fleet boats data: {str(e)}")
    print(f"Error: {str(e)}")
    raise
