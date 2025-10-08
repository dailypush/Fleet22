# GitHub Actions Workflow Update

**Date:** October 7, 2025  
**Branch:** feature/rearrange  
**File:** `.github/workflows/run-python-scripts.yml`

## Summary

Updated the GitHub Actions workflow to match the new directory structure and modernized scripts from the workspace reorganization.

## Changes Made

### 1. Updated Requirements Path
- **Old:** `scraper/requirements.txt`
- **New:** `scripts/requirements.txt`
- **Applied to:** All 4 jobs (fetch-sail-tags, fetch-owners-status, fetch-fleet-boats, process-and-commit)

### 2. Updated Script Execution Paths

#### Sail Tags Job
- **Old:** `python scraper/SailTags.py`
- **New:** `python -m scripts.scrapers.scrape_sail_tags`
- **Output:** `data/sails/sail_tags.json` (was `data/sail_tags.json`)

#### Owners Status Job
- **Old:** `python scraper/getOwnersStatus.py`
- **New:** `python -m scripts.scrapers.scrape_owner_status`
- **Output:** `data/members/j105_members_status.json` (was `data/j105_members_status.json`)

#### Fleet Boats Job
- **Old:** `python scraper/fleetBoats_github_actions.py`
- **New:** `python -m scripts.scrapers.scrape_fleet_boats`
- **Output:** `data/boats/boats_fleet22.json` (was `data/boats_fleet22.json`)
- **Note:** Updated member.html check to look in `pages/members.html` first, then fallback to root

### 3. Updated Validator and Processor Paths

#### Validation Step
- **Old:** `python scraper/validate_data.py`
- **New:** `python -m scripts.validators.validate_fleet_data`

#### Data Processor Step
- **Old:** `python scraper/combineFleetSailOwner.py`
- **New:** `python -m scripts.processors.combine_data_sources`
- **Outputs:** 
  - `data/combined/combined_fleet_data.json` (was `data/combined_fleet_data.json`)
  - `data/combined/fleet_statistics.json` (was `data/fleet_statistics.json`)

### 4. Updated Data Directory Structure

Created organized subdirectories:
- `data/boats/` - Fleet boat data
- `data/sails/` - Sail certification tags
- `data/members/` - Membership status data
- `data/combined/` - Processed combined data

### 5. Updated All File References

Updated all references in:
- Artifact download/upload paths
- File existence checks
- Git diff operations
- Commit message generation
- Data report generation
- Final artifact uploads

### 6. Updated Log File Path
- **Old:** `scraper/scraping.log`
- **New:** `logs/scraping.log`

## Testing Status

### Prerequisites for Testing
1. ✅ Scripts have been refactored and tested locally:
   - `scripts/scrapers/scrape_sail_tags.py` - 8,091 records
   - `scripts/scrapers/scrape_owner_status.py` - 835 records
   - `scripts/scrapers/scrape_fleet_boats.py` - 20 boats

2. ⏳ **Pending:** Test workflow scripts still need refactoring:
   - `scripts/validators/validate_fleet_data.py` - Not yet created/updated
   - `scripts/processors/combine_data_sources.py` - Not yet created/updated

### Testing Plan
1. **Before Merge:** 
   - Create/refactor validator and processor scripts
   - Test workflow on feature branch with manual trigger
   - Verify all artifacts are generated correctly
   - Check git commit and push functionality

2. **After Merge:**
   - Monitor first automated run (Monday 00:00 UTC)
   - Verify data is committed to correct paths
   - Check artifact retention

## Next Steps

1. **Immediate:**
   - Refactor `scraper/validate_data.py` → `scripts/validators/validate_fleet_data.py`
   - Refactor `scraper/combineFleetSailOwner.py` → `scripts/processors/combine_data_sources.py`
   - Update both scripts to use new data paths and utility modules

2. **Testing:**
   - Trigger workflow manually using "Run workflow" button
   - Check workflow logs for any path-related errors
   - Verify generated artifacts

3. **Final Steps:**
   - Create pull request to merge feature/rearrange → main
   - Document all changes in PR description
   - Merge after successful workflow test
   - Monitor first scheduled run

## Impact

### Benefits
- ✅ Consistent with new directory structure
- ✅ Uses Python module imports (more reliable)
- ✅ Better organized data outputs
- ✅ Centralized logging
- ✅ Easier to maintain and debug

### Risks
- ⚠️ Workflow will fail if validator/processor scripts aren't ready
- ⚠️ Old data locations will no longer be updated
- ⚠️ External tools/scripts referencing old paths need updates

## Rollback Plan

If issues occur after merge:
1. Revert this commit
2. Workflow will use old paths temporarily
3. Fix issues in feature branch
4. Re-merge when ready

## Related Files

This update is part of the larger workspace reorganization:
- See `WORKSPACE_REORGANIZATION.md` for overall structure changes
- See `SCRIPTS_ANALYSIS.md` for script analysis and planning
- See `PHASE1_COMPLETE.md` for completed script refactoring details
