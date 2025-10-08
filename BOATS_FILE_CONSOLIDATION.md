# Boats File Consolidation Summary

**Date:** October 7, 2025

## Problem
There were two versions of the boats data file:
1. `/data/boats/boats_fleet22.json` - Being auto-updated by scripts
2. `/data/boats_fleet22.json` - Root-level duplicate for "GitHub Pages compatibility"

This created confusion about which file was the source of truth and could lead to data inconsistencies.

## Solution
Consolidated to a **single source of truth**: `data/boats/boats_fleet22.json`

## Changes Made

### 1. Files Updated

#### `/pages/fleetdues.html`
- Updated API fetch path from `data/boats_fleet22.json` to `data/boats/boats_fleet22.json`
- Updated commit history path for last modified date

#### `/FLEET_DUES_FORMAT.md`
- Removed reference to "Root Copy" file
- Updated File Locations section to show single source of truth
- Updated JavaScript example to use correct path
- Clarified that file is auto-updated by GitHub Actions

#### `/QUICK_REFERENCE_DUES_UPDATE.md`
- Removed manual copy step from update instructions
- Simplified git commit process to only add the single file
- Updated examples to reflect single file workflow

#### `/README.md`
- Changed `data/boats_fleet22.json` reference to `data/boats/boats_fleet22.json`
- Added note that file is automatically updated

#### `/scripts/utils/reset_dues_season.py`
- Removed logic that updated the root-level duplicate file
- Removed `root_file` variable
- Simplified to only work with the canonical file location

#### `/.gitignore`
- Added `data/boats_fleet22.json` to prevent accidental recreation
- Added comment explaining it's a duplicate that should not be used

### 2. File Removed
- Deleted `/data/boats_fleet22.json` (the root-level duplicate)

## Benefits

1. **Single Source of Truth**: Only one file to maintain and update
2. **No Sync Issues**: Eliminates risk of files being out of sync
3. **Clearer Documentation**: Simpler instructions for users
4. **Automatic Updates**: GitHub Actions workflow already updates the correct location
5. **Prevention**: Added to .gitignore to prevent recreation

## Migration Path

For anyone with local changes:

1. If you edited `/data/boats_fleet22.json` (root level):
   - Copy your changes to `/data/boats/boats_fleet22.json`
   - Delete `/data/boats_fleet22.json`
   
2. Update any local scripts or bookmarks:
   - Change path from `data/boats_fleet22.json` to `data/boats/boats_fleet22.json`

3. Pull latest changes:
   ```bash
   git pull origin main
   ```

## File Location Reference

### Current (Correct)
- **Data File**: `data/boats/boats_fleet22.json`
- **Web API**: `https://api.github.com/repos/dailypush/Fleet22/contents/data/boats/boats_fleet22.json`
- **Commits API**: `https://api.github.com/repos/dailypush/Fleet22/commits?path=data/boats/boats_fleet22.json`

### Deprecated (Do Not Use)
- ~~`data/boats_fleet22.json`~~ - Removed and added to .gitignore

## Testing Checklist

- [x] HTML page fetches from correct location
- [x] Documentation updated to reflect single file
- [x] Scripts reference correct path
- [x] Duplicate file removed
- [x] Gitignore updated to prevent recreation
- [x] README.md references correct location

## Related Documentation

- `FLEET_DUES_FORMAT.md` - Fleet dues data structure and format
- `QUICK_REFERENCE_DUES_UPDATE.md` - Quick guide for updating dues
- `scripts/utils/reset_dues_season.py` - Season reset utility
- `scripts/scrapers/scrape_fleet_boats.py` - Auto-update script

## Notes

- The GitHub Actions workflow (`.github/workflows/run-python-scripts.yml`) already uses the correct path
- All scripts in the `scripts/` directory use the centralized path from `utils/path_utils.py`
- The `path_utils.py` module defines `BOATS_FILE = BOATS_DATA / "boats_fleet22.json"` which correctly points to `data/boats/boats_fleet22.json`
