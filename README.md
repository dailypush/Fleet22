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
  - `css/`: Website stylesheets
  - `documents/`: Sponsorship packets and other downloadable documents
  - `fleet22_logos/`: Fleet 22 branding assets
  - `images/`: Website images
  - `na_logos/` and `na_sponsors/`: North Americans event assets
- `data/`: JSON data files containing fleet information
  - `boats/`: Fleet 22 boat data
  - `members/`: J105 class membership and owner status data
  - `sails/`: Sail tag certification data
  - `combined/`: Unified datasets combining multiple sources
  - `payments/`: Payment tracking and dues information
  - `races/`: Race results and statistics
  - `calendar/`: Event and regatta schedules
- `pages/`: Website HTML pages
  - Fleet dues, members, classifieds, and news sections
- `scripts/`: Modular Python scripts for data management
  - `scrapers/`: Web scrapers for external data sources
  - `processors/`: Data combination and processing tools
  - `validators/`: Data validation and quality checks
  - `analysis/`: Data analysis and visualization scripts
  - `generators/`: Report and document generators
  - `reports/`: Payment and status reporting tools
  - `utils/`: Shared utilities (logging, paths, data loading)
- `logs/`: Application logs for scraping, processing, and analysis
- `tools/`: Development and testing utilities

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Running the Scripts Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Fleet22/Fleet22_us.git
   cd Fleet22_us
   ```

2. Install the required Python dependencies:
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

3. Run the data scrapers:
   ```bash
   # Scrape J105 class membership and owner status
   python -m scrapers.scrape_owner_status
   
   # Scrape sail certification data
   python -m scrapers.scrape_sail_tags
   
   # Scrape Fleet 22 boat information
   python -m scrapers.scrape_fleet_boats
   ```

4. Process and combine data:
   ```bash
   # Combine data from multiple sources
   python -m processors.combine_data_sources
   
   # Update payment status
   python -m processors.update_payment_status
   ```

5. Validate data integrity:
   ```bash
   # Validate all JSON data files
   python -m validators.validate_fleet_data
   
   # Check sail purchase limits
   python -m validators.check_sail_limits
   ```

6. Generate reports:
   ```bash
   # Generate payment follow-up reports
   python -m reports.generate_payment_followup
   ```

### Data Analysis Tools

The repository includes several data analysis tools:

1. **Sail Purchase Heatmaps**: Visualize sail purchase patterns by hull number
   ```bash
   cd analysis/heatmaps
   python sailHeatMap.py
   ```

2. **Sailmaker Trends Analysis**: Analyze sailmaker purchase trends over time
   ```bash
   cd scripts
   python -m analysis.analyze_sailmaker_trends
   ```

3. **Interactive Visualizations**:
   - `analysis/heatmap.html` - Interactive sail purchase heatmap
   - `analysis/treemap/treemap.html` - Sail tag data treemap visualization
   - `analysis/sail_analysis_heatmap.html` - Comprehensive sail analysis

## Script Features

### Data Quality & Integrity
- **HTML Entity Decoding**: All scrapers properly decode HTML entities (`&copy;`, `&amp;`, etc.) to prevent formatting issues in owner names and other text fields
- **Automatic Backups**: Data files are automatically backed up before updates
- **Data Validation**: Comprehensive validation checks ensure data integrity
- **Error Logging**: Detailed logging to `logs/` directory for troubleshooting

### Modular Architecture
The scripts are organized into functional modules:
- **Scrapers**: Independent data collection from external sources
- **Processors**: Data transformation and combination logic
- **Validators**: Data quality checks and rule enforcement
- **Generators**: Report and document creation
- **Utils**: Shared functionality (paths, logging, data I/O)

## Workflow Automation

The data collection process is automated using GitHub Actions, which:
- Runs weekly on Mondays at midnight UTC
- Runs on pushes to the main branch
- Can be manually triggered with force update option
- Validates data integrity before committing
- Combines data from multiple sources into a unified dataset
- Only commits changes when data files are modified
- Provides detailed logs and statistics as workflow artifacts
- Creates automatic backups of data before updates

### Managing Workflow Runs

You can manually trigger workflow runs from the GitHub Actions tab in the repository.
For scheduled runs, the workflow is configured in `.github/workflows/run-python-scripts.yml`.

## Troubleshooting

### Common Issues

**Import Errors**: Make sure you're running scripts from the `scripts/` directory or using the `-m` module syntax:
```bash
cd scripts
python -m scrapers.scrape_owner_status
```

**SSL Certificate Warnings**: The J105 archive site may have SSL certificate issues. The scrapers handle this by disabling SSL verification (for archive.j105.org only).

**Log Files**: Check the `logs/` directory for detailed error messages:
- `logs/scraping.log` - Web scraper activity
- `logs/data_management.log` - Data processing and validation
- `logs/reports.log` - Report generation

**Data Validation Failures**: Run the validator to identify issues:
```bash
python -m validators.validate_fleet_data
```

### Data Recovery

If data becomes corrupted, automatic backups are created in the same directory with timestamps:
- `data/members/j105_members_status_backup_YYYYMMDD_HHMMSS.json`

Restore by copying the backup over the current file.

### Data Files

The following JSON data files are automatically maintained:

**Member Data:**
- `data/members/j105_members_status.json`: J105 class membership and owner status (automatically scraped)

**Sail Data:**
- `data/sails/sail_tags.json`: Sail certification data for all J/105 boats (automatically scraped)

**Fleet Data:**
- `data/boats/boats_fleet22.json`: Fleet 22 specific boat information (automatically updated)
- `data/boats/*.json`: Individual boat data files

**Combined Data:**
- `data/combined/combined_fleet_data.json`: Unified dataset combining all sources
- `data/combined/fleet_statistics.json`: Statistical summaries

**Payment Data:**
- `data/payments/`: Payment tracking and dues status
- Payment summary reports and follow-up lists

**Race Data:**
- `data/races/`: Race results and event data

## Contributing

Contributions to improve the website or data tools are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

See the [LICENSE](LICENSE) file for details.