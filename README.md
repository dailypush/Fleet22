# Fleet22_us Website

![Run Python Scripts](https://github.com/USER_NAME/Fleet22_us/actions/workflows/run-python-scripts.yml/badge.svg)

## About
This repository contains the website for Fleet 22 of the J/105 class sailing association, along with data analysis tools and web scrapers to maintain up-to-date information.

## Automated Data Collection
This repository includes automated Python scripts that run daily to collect:
- Sail tag information
- J/105 class membership status
- Fleet boat information
- Combined unified dataset with all boat information

Data is automatically updated via GitHub Actions and committed to the repository.

## Repository Structure
- `analysis/`: Visualization and analysis scripts including heatmaps
- `assets/`: Website styles, images, and downloadable documents
- `data/`: JSON data files containing fleet information
- `scraper/`: Python scripts for data collection
- `documents/`: Forms and documentation

## Development

### Running the Scrapers Locally
To run the scrapers locally:

1. Install the required Python dependencies:
   ```
   pip install -r scraper/requirements.txt
   ```

2. Run the individual scripts:
   ```
   python scraper/SailTags.py
   python scraper/getOwnersStatus.py
   python scraper/fleetBoats.py
   ```

3. Run data validation:
   ```
   python scraper/validate_data.py
   ```

4. Generate combined dataset:
   ```
   python scraper/combineFleetSailOwner.py
   ```

### Workflow Automation
The data collection process is automated using GitHub Actions, which:
- Runs daily at midnight UTC
- Runs on pushes to the main branch
- Can be manually triggered with force update option
- Validates data integrity before committing
- Combines data from multiple sources into a unified dataset
- Only commits changes when data files are modified
- Provides detailed logs and statistics as workflow artifacts

### Data Files
The following JSON data files are automatically maintained:
- `data/sail_tags.json`: Contains sail tag information for all J/105 boats
- `data/j105_members_status.json`: Contains J/105 class membership status
- `data/boats_fleet22.json`: Contains Fleet 22 specific boat information
- `data/combined_fleet_data.json`: Unified dataset combining all sources
- `data/fleet_statistics.json`: Statistical information about the fleet

## License
See the [LICENSE](LICENSE) file for details.