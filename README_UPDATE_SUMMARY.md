# README Update Summary

**Date:** October 7, 2025

## Changes Made

### 1. Updated Repository Structure Section
- Added detailed breakdown of `data/` subdirectories (boats, members, sails, combined, payments, races, calendar)
- Added `pages/` section for website HTML pages
- Expanded `scripts/` structure to show all module categories:
  - scrapers, processors, validators, analysis, generators, reports, utils
- Added `logs/` and `tools/` directories
- Added `assets/css/` subdirectory

### 2. Modernized "Running the Scripts Locally" Section
- Changed from `pip install -r scraper/requirements.txt` to `cd scripts && pip install -r requirements.txt`
- Updated all script execution examples to use Python module syntax:
  - `python -m scrapers.scrape_owner_status` (instead of `python scraper/getOwnersStatus.py`)
  - `python -m scrapers.scrape_sail_tags`
  - `python -m scrapers.scrape_fleet_boats`
- Added processor commands:
  - `python -m processors.combine_data_sources`
  - `python -m processors.update_payment_status`
- Added validator commands:
  - `python -m validators.validate_fleet_data`
  - `python -m validators.check_sail_limits`
- Added report generation command:
  - `python -m reports.generate_payment_followup`

### 3. Enhanced Data Analysis Tools Section
- Updated heatmap path to `analysis/heatmaps/`
- Added sailmaker trends analysis command
- Added list of interactive visualization HTML files:
  - heatmap.html
  - treemap.html
  - sail_analysis_heatmap.html

### 4. Added "Script Features" Section (NEW)
Documented key capabilities:
- **Data Quality & Integrity**:
  - HTML entity decoding (fixes `&copy;`, `&amp;` issues)
  - Automatic backups with timestamps
  - Comprehensive data validation
  - Detailed error logging
- **Modular Architecture**:
  - Clear separation of concerns across modules
  - Independent, reusable components

### 5. Enhanced Workflow Automation Section
- Added "Creates automatic backups of data before updates" to the feature list

### 6. Added "Troubleshooting" Section (NEW)
- **Common Issues**:
  - Import errors and how to fix them
  - SSL certificate warnings explanation
  - Log file locations and purposes
  - Data validation failure handling
- **Data Recovery**:
  - Explanation of automatic backup naming convention
  - Instructions for restoring from backup

### 7. Reorganized "Data Files" Section
Now organized by category:
- **Member Data**: j105_members_status.json location
- **Sail Data**: sail_tags.json location
- **Fleet Data**: boats_fleet22.json and individual boat files
- **Combined Data**: unified datasets and statistics
- **Payment Data**: payment tracking files
- **Race Data**: race results location

## Key Improvements

1. **Clarity**: Script paths and commands now match the actual refactored structure
2. **Completeness**: All major script categories are documented with examples
3. **Troubleshooting**: Added practical solutions for common issues
4. **Data Organization**: Clear explanation of data file locations and purposes
5. **HTML Entity Handling**: Documented the fix for HTML entity issues in scraped data

## Files Modified

- `README.md` - Main repository documentation

## Related Updates

This README update reflects the following improvements to the codebase:
1. Scripts refactored into modular structure (scrapers, processors, validators, etc.)
2. HTML entity decoding added to `scrape_owner_status.py`
3. Centralized utilities (path_utils, logger, data_loader)
4. Comprehensive logging infrastructure
5. Automatic backup system for data files

## Next Steps

Users can now:
1. Easily understand the repository structure
2. Run scripts using proper module syntax
3. Troubleshoot common issues independently
4. Locate and understand all data files
5. Take advantage of automatic backups and data validation
