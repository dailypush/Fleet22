from bs4 import BeautifulSoup
import json

# Load the HTML content from the file
file_path = '../members.html'
with open(file_path, 'r') as file:
    html_content = file.read()

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table by class name
table = soup.find('table', {'class': 'table table-striped'})

# Extract data
data_list = []

# Assuming the first row of the table is headers
headers = [header.text.strip() for header in table.find_all('th')]

# Process each row of the table
for row in table.find_all('tr')[1:]:  # skip the header row
    cols = row.find_all('td')
    row_data = {headers[i]: col.text.strip() for i, col in enumerate(cols)}
    data_list.append(row_data)

# Convert the list to JSON
json_output = json.dumps(data_list, indent=4)

# Specify the JSON output file path
output_file_path = 'boats_fleet22.json'

# Write the JSON data to a file
with open(output_file_path, 'w') as json_file:
    json_file.write(json_output)

output_file_path
