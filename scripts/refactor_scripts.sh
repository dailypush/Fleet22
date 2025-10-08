#!/bin/bash
# Quick Script Refactoring - Immediate Improvements
# Implements naming consistency and structure improvements
# Created: October 7, 2025

set -e

echo "🔧 Fleet22 Scripts Quick Refactoring"
echo "===================================="
echo ""

BASE_DIR="/Users/chad/Projects/Fleet22_us/scripts"
cd "$BASE_DIR"

# Confirmation
echo "This script will:"
echo "  1. Rename scripts for consistency (snake_case)"
echo "  2. Create new directory structure"
echo "  3. Create utility modules"
echo "  4. Update requirements.txt"
echo ""
read -p "Continue? (yes/no): " response

if [ "$response" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "📝 Phase 1: Renaming Scripts"
echo "===================================="

# Rename scrapers
cd scrapers
[ -f "SailTags.py" ] && mv "SailTags.py" "scrape_sail_tags.py" && echo "✓ Renamed SailTags.py → scrape_sail_tags.py"
[ -f "getOwnersStatus.py" ] && mv "getOwnersStatus.py" "scrape_owner_status.py" && echo "✓ Renamed getOwnersStatus.py → scrape_owner_status.py"
[ -f "fleetBoats.py" ] && mv "fleetBoats.py" "scrape_fleet_boats_local.py" && echo "✓ Renamed fleetBoats.py → scrape_fleet_boats_local.py"
[ -f "fleetBoats_github_actions.py" ] && mv "fleetBoats_github_actions.py" "scrape_fleet_boats.py" && echo "✓ Renamed fleetBoats_github_actions.py → scrape_fleet_boats.py"
[ -f "combineFleetSailOwner.py" ] && mv "combineFleetSailOwner.py" "combine_data_sources.py" && echo "✓ Renamed combineFleetSailOwner.py → combine_data_sources.py"
[ -f "yachtscoring_extract_ws_number.py" ] && mv "yachtscoring_extract_ws_number.py" "extract_world_sailing_numbers.py" && echo "✓ Renamed yachtscoring_extract_ws_number.py → extract_world_sailing_numbers.py"

cd ..

# Rename utilities
cd utilities
[ -f "fleet22_payment_status.py" ] && mv "fleet22_payment_status.py" "update_payment_status.py" && echo "✓ Renamed fleet22_payment_status.py → update_payment_status.py"
[ -f "sail_limit_checker.py" ] && mv "sail_limit_checker.py" "check_sail_limits.py" && echo "✓ Renamed sail_limit_checker.py → check_sail_limits.py"
[ -f "validate_data.py" ] && mv "validate_data.py" "validate_fleet_data.py" && echo "✓ Renamed validate_data.py → validate_fleet_data.py"

cd ..

# Rename analysis
cd analysis
[ -f "SailmakerAnnualSailpurchases.py" ] && mv "SailmakerAnnualSailpurchases.py" "analyze_sailmaker_trends.py" && echo "✓ Renamed SailmakerAnnualSailpurchases.py → analyze_sailmaker_trends.py"

cd ..

echo ""
echo "📁 Phase 2: Creating New Directory Structure"
echo "===================================="

# Create new directories
mkdir -p utils
mkdir -p processors
mkdir -p validators
echo "✓ Created new directories: utils/, processors/, validators/"

# Move files to better locations
if [ -f "scrapers/combine_data_sources.py" ]; then
    mv scrapers/combine_data_sources.py processors/
    echo "✓ Moved combine_data_sources.py → processors/"
fi

if [ -f "utilities/update_payment_status.py" ]; then
    mv utilities/update_payment_status.py processors/
    echo "✓ Moved update_payment_status.py → processors/"
fi

if [ -f "utilities/validate_fleet_data.py" ]; then
    mv utilities/validate_fleet_data.py validators/
    echo "✓ Moved validate_fleet_data.py → validators/"
fi

if [ -f "utilities/check_sail_limits.py" ]; then
    mv utilities/check_sail_limits.py validators/
    echo "✓ Moved check_sail_limits.py → validators/"
fi

# Remove empty utilities directory if empty
rmdir utilities 2>/dev/null && echo "✓ Removed empty utilities directory" || echo "ℹ  utilities directory still has files"

echo ""
echo "🔧 Phase 3: Creating Utility Modules"
echo "===================================="

# Create __init__.py files
touch scrapers/__init__.py
touch processors/__init__.py
touch validators/__init__.py
touch analysis/__init__.py
touch utils/__init__.py
echo "✓ Created __init__.py in all directories"

# Create path_utils.py
cat > utils/path_utils.py << 'EOF'
"""Centralized path management for Fleet22 scripts."""
from pathlib import Path

# Project root (3 levels up from utils/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Data subdirectories
BOATS_DATA = DATA_DIR / "boats"
SAILS_DATA = DATA_DIR / "sails"
MEMBERS_DATA = DATA_DIR / "members"
RACES_DATA = DATA_DIR / "races"
CALENDAR_DATA = DATA_DIR / "calendar"
PAYMENTS_DATA = DATA_DIR / "payments"

# Commonly used files
BOATS_FILE = BOATS_DATA / "boats_fleet22.json"
SAIL_TAGS_FILE = SAILS_DATA / "sail_tags.json"
MEMBERS_FILE = MEMBERS_DATA / "j105_members_status.json"
COMBINED_FILE = BOATS_DATA / "combined_fleet_data.json"

def ensure_directories():
    """Create all required directories if they don't exist."""
    for directory in [BOATS_DATA, SAILS_DATA, MEMBERS_DATA, 
                      RACES_DATA, CALENDAR_DATA, PAYMENTS_DATA, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def get_backup_path(original_file: Path) -> Path:
    """Generate a timestamped backup path for a file."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return original_file.parent / f"{original_file.stem}_backup_{timestamp}{original_file.suffix}"

if __name__ == "__main__":
    # Test paths
    ensure_directories()
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Boats File: {BOATS_FILE}")
EOF

echo "✓ Created utils/path_utils.py"

# Create logger.py
cat > utils/logger.py << 'EOF'
"""Centralized logging configuration for Fleet22 scripts."""
import logging
from pathlib import Path
from .path_utils import LOGS_DIR

def setup_logger(name: str, log_file: str = "scraping.log", 
                 level: int = logging.INFO) -> logging.Logger:
    """
    Setup a logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Log file name (default: scraping.log)
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Ensure log directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / log_file
    
    # File handler
    file_handler = logging.FileHandler(log_path, mode='a')
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
EOF

echo "✓ Created utils/logger.py"

# Create data_loader.py
cat > utils/data_loader.py << 'EOF'
"""Standardized data loading utilities for Fleet22 scripts."""
import json
from pathlib import Path
from typing import List, Dict, Any
from .logger import setup_logger

logger = setup_logger(__name__)

def load_json(filepath: Path) -> List[Dict[str, Any]]:
    """
    Load JSON data from a file.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Parsed JSON data as list of dictionaries
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data) if isinstance(data, list) else 'data'} from {filepath.name}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        raise

def save_json(data: Any, filepath: Path, indent: int = 4, 
              create_backup: bool = True) -> None:
    """
    Save data as JSON to a file.
    
    Args:
        data: Data to save
        filepath: Path to save to
        indent: JSON indentation (default: 4)
        create_backup: Whether to create backup of existing file
    """
    # Create backup if file exists
    if create_backup and filepath.exists():
        from .path_utils import get_backup_path
        backup_path = get_backup_path(filepath)
        import shutil
        shutil.copy2(filepath, backup_path)
        logger.info(f"Created backup: {backup_path.name}")
    
    # Save new data
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    
    logger.info(f"Saved {len(data) if isinstance(data, list) else 'data'} to {filepath.name}")
EOF

echo "✓ Created utils/data_loader.py"

echo ""
echo "📦 Phase 4: Updating requirements.txt"
echo "===================================="

# Update requirements.txt
cat > requirements.txt << 'EOF'
# Fleet22 Scripts Dependencies
# Updated: October 7, 2025

# Web scraping
beautifulsoup4>=4.12.0
requests>=2.31.0
lxml>=5.0.0

# Data processing
pandas>=2.1.0

# Visualization
matplotlib>=3.8.0

# Progress bars
tqdm>=4.66.0

# CLI
click>=8.1.0

# Configuration
pyyaml>=6.0.1
EOF

echo "✓ Updated requirements.txt with current versions"

echo ""
echo "📄 Phase 5: Creating Documentation"
echo "===================================="

# Create README for scripts
cat > README.md << 'EOF'
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
EOF

echo "✓ Created scripts/README.md"

echo ""
echo "===================================="
echo "✅ Quick Refactoring Complete!"
echo "===================================="
echo ""
echo "Summary of changes:"
echo "  • Renamed 10 scripts for consistency"
echo "  • Created 4 new directories"
echo "  • Created 3 utility modules"
echo "  • Updated requirements.txt"
echo "  • Created README.md"
echo ""
echo "📊 New Structure:"
echo "  scripts/"
echo "  ├── scrapers/           (6 scripts)"
echo "  ├── processors/         (2 scripts)"
echo "  ├── validators/         (2 scripts)"
echo "  ├── analysis/           (1 script)"
echo "  └── utils/              (3 modules)"
echo ""
echo "⚠️  Next steps:"
echo "  1. Update import statements in scripts"
echo "  2. Test all scripts with new paths"
echo "  3. Update GitHub Actions workflows"
echo "  4. Commit changes: git add -A && git commit -m 'Refactor scripts structure'"
echo ""
