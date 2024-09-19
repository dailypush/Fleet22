from bs4 import BeautifulSoup

def extract_sailing_data(html_file_path):
    # Open and read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize an empty list to store the crew names and World Sailing numbers
    sailing_data = []

    # Find all rows in the table (assuming data is within table rows)
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        # Check if the row has enough cells and contains a link in the expected position
        if len(cells) > 4 and cells[4].find('a'):
            crew_name = cells[1].text.strip()
            world_sailing_number = cells[4].find('a').text.strip()
            sailing_data.append((crew_name, world_sailing_number))

    return sailing_data

def main():
    file_path = 'path_to_your_html_file.html'  # Specify the path to your HTML file
    data = extract_sailing_data(file_path)
    
    # Print the extracted data
    for crew, number in data:
        print(f"Crew Name: {crew}, World Sailing Number: {number}")

if __name__ == "__main__":
    main()
