# Fleet22_us Website

![Run Python Scripts](https://github.com/dailypush/Fleet22_us/actions/workflows/run-python-scripts.yml/badge.svg)

## About
This repository contains the official website and data management tools for Fleet 22 of the J/105 class sailing association. It includes web scrapers to maintain up-to-date fleet information, data analysis tools, visualization scripts, and website resources.

## Website Features
- Fleet membership information
- Sailing event details and results
- North Americans 2024 regatta information
- Fleet news and classifieds
- Media resources and sponsorship information

## Automated Data Collection
This repository includes automated Python scripts that run weekly to collect:
- Sail tag information from the J/105 class registry
- J/105 class membership status
- Fleet 22 specific boat information
- Fleet dues and payment status
- Combined unified dataset with all boat information

Data is automatically updated via GitHub Actions and committed to the repository every Monday at midnight UTC.

## Repository Structure
- `analysis/`: Data visualization tools including heatmaps and sail purchase trend analysis
  - `heatmaps/`: Hull-specific sail purchase heatmaps
  - `treemap/`: Interactive treemap of sail tag data
- `assets/`: Website styles, images, and downloadable resources
  - `documents/`: Sponsorship packets and other downloadable documents
  - `fleet22_logos/`: Fleet 22 branding assets
  - `images/`: Website images
  - `na_logos/` and `na_sponsors/`: North Americans event assets
- `data/`: JSON data files containing fleet information
  - Automatically maintained boat, membership and sail data
  - North Americans 2024 race results
  - Payment reports and summaries
- `documents/`: Forms, checklists, and interactive tools
  - Crew weigh-in forms
  - Sail declaration forms
  - North Americans inspection checklists
- `scraper/`: Python and Go scripts for data collection
  - Core data collection workflows
  - Validation tools
  - Data processing utilities

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Running the Scrapers Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Fleet22/Fleet22_us.git
   cd Fleet22_us
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r scraper/requirements.txt
   ```

3. Run the individual scripts:
   ```bash
   python scraper/SailTags.py
   python scraper/getOwnersStatus.py
   python scraper/fleetBoats.py
   ```

4. Run data validation:
   ```bash
   python scraper/validate_data.py
   ```

5. Generate combined dataset:
   ```bash
   python scraper/combineFleetSailOwner.py
   ```

### Data Analysis Tools

The repository includes several data analysis tools in the `analysis/` directory:

1. **Sail Purchase Heatmaps**: Visualize sail purchase patterns by hull number
   ```bash
   cd analysis
   python sailHeatMap.py
   ```

2. **Sailmaker Annual Purchase Trends**: Analyze trends in sailmaker preference
   ```bash
   cd analysis
   python SailmakerAnnualSailpurchases.py
   ```

## Workflow Automation

The data collection process is automated using GitHub Actions, which:
- Runs weekly on Mondays at midnight UTC
- Runs on pushes to the main branch
- Can be manually triggered with force update option
- Validates data integrity before committing
- Combines data from multiple sources into a unified dataset
- Only commits changes when data files are modified
- Provides detailed logs and statistics as workflow artifacts

### Managing Workflow Runs

You can manually trigger workflow runs from the GitHub Actions tab in the repository.
For scheduled runs, the workflow is configured in `.github/workflows/run-python-scripts.yml`.

### Data Files

The following JSON data files are automatically maintained:
- `data/sail_tags.json`: Contains sail tag information for all J/105 boats
- `data/j105_members_status.json`: Contains J/105 class membership status
- `data/boats_fleet22.json`: Contains Fleet 22 specific boat information
- `data/combined_fleet_data.json`: Unified dataset combining all sources
- `data/fleet_statistics.json`: Statistical information about the fleet

## Contributing

Contributions to improve the website or data tools are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

See the [LICENSE](LICENSE) file for details.