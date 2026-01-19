#!/bin/bash

# Fleet22 Data Update Script
# Updates all JSON data sources with a single command
# Usage: ./update_all_data.sh

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Fleet22 Data Update - All Scrapers${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${YELLOW}Error: Virtual environment not found at $VENV_PYTHON${NC}"
    echo "Please run: cd $PROJECT_DIR && python -m venv .venv && pip install -r scripts/requirements.txt"
    exit 1
fi

cd "$SCRIPT_DIR"

# Run fleet boats scraper
echo -e "${BLUE}[1/3]${NC} Running Fleet Boats Scraper..."
if "$VENV_PYTHON" scrapers/scrape_fleet_boats.py; then
    echo -e "${GREEN}✓ Fleet Boats updated${NC}"
else
    echo -e "${YELLOW}✗ Fleet Boats scraper failed${NC}"
    exit 1
fi
echo ""

# Run sail tags scraper
echo -e "${BLUE}[2/3]${NC} Running Sail Tags Scraper..."
if "$VENV_PYTHON" scrapers/scrape_sail_tags.py; then
    echo -e "${GREEN}✓ Sail Tags updated${NC}"
else
    echo -e "${YELLOW}✗ Sail Tags scraper failed${NC}"
    exit 1
fi
echo ""

# Run owner status scraper
echo -e "${BLUE}[3/3]${NC} Running Owner Status Scraper..."
if "$VENV_PYTHON" scrapers/scrape_owner_status.py; then
    echo -e "${GREEN}✓ Owner Status updated${NC}"
else
    echo -e "${YELLOW}✗ Owner Status scraper failed${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ All data sources updated successfully!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
