# Fleet22 Scripts

Automated data collection, processing, and analysis scripts for Fleet 22 J105 racing data.

## Directory Structure

```
scripts/
├── scrapers/        # Web scrapers for external data sources
├── processors/      # Data combination and processing
├── validators/      # Data validation and quality checks
├── analysis/        # Data analysis and visualization
└── utils/          # Shared utilities and helpers
```

## Quick Start

### Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### Run Scrapers

```bash
# Scrape fleet boats data
python -m scrapers.scrape_fleet_boats

# Scrape sail tags
python -m scrapers.scrape_sail_tags

# Scrape owner status
python -m scrapers.scrape_owner_status
```

### Process Data

```bash
# Combine data sources
python -m processors.combine_data_sources

# Update payment status
python -m processors.update_payment_status
```

### Validate Data

```bash
# Validate all fleet data
python -m validators.validate_fleet_data

# Check sail purchase limits
python -m validators.check_sail_limits
```

## Utilities

The `utils/` module provides shared functionality:

- `path_utils.py` - Centralized path management
- `logger.py` - Consistent logging setup
- `data_loader.py` - Standard data loading/saving

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

We follow PEP 8. Format code with:

```bash
black scripts/
isort scripts/
```

## Scripts Reference

### Scrapers

- **scrape_fleet_boats.py** - Scrapes boat data from members page
- **scrape_sail_tags.py** - Scrapes sail certification data
- **scrape_owner_status.py** - Scrapes owner/membership status
- **extract_world_sailing_numbers.py** - Extracts WS numbers from race results

### Processors

- **combine_data_sources.py** - Combines fleet, sail, and owner data
- **update_payment_status.py** - Updates payment status in boat records

### Validators

- **validate_fleet_data.py** - Validates JSON data structure and integrity
- **check_sail_limits.py** - Checks sail purchase limits per class rules

### Analysis

- **analyze_sailmaker_trends.py** - Analyzes sailmaker purchase trends over time

## Configuration

Paths and settings are managed in `utils/path_utils.py`. Update this file to change:

- Data directory locations
- File naming patterns
- Backup strategies

## Logging

All scripts log to `logs/scraping.log`. Configure logging in `utils/logger.py`.

## License

Part of the Fleet22 project. See main repository LICENSE.
