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
