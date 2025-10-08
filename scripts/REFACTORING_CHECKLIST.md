# Scripts Refactoring - Next Steps Checklist

**Status**: ✅ Phase 1 Complete (Structure & Utilities Created)  
**Date**: October 7, 2025

## ✅ Completed

- [x] Renamed all scripts to snake_case naming convention
- [x] Created new directory structure (utils/, processors/, validators/)
- [x] Created utility modules (path_utils.py, logger.py, data_loader.py)
- [x] Updated requirements.txt with current versions
- [x] Created scripts/README.md documentation
- [x] Added __init__.py to all packages

## 🔄 In Progress - Import Updates

### Priority 1: Update Core Scripts (DO THIS FIRST)

1. **Update scrape_sail_tags.py** ✅ Script ready
   ```bash
   cd scripts
   chmod +x update_imports.sh
   ./update_imports.sh
   ```

2. **Manually update remaining scrapers** (5 scripts)
   - [ ] `scrape_fleet_boats.py` - Update logging, paths
   - [ ] `scrape_fleet_boats_local.py` - Update logging, paths  
   - [ ] `scrape_owner_status.py` - Update logging, paths
   - [ ] `extract_world_sailing_numbers.py` - Fix undefined variables, update paths

3. **Update processors** (2 scripts)
   - [ ] `combine_data_sources.py` - Use path_utils, data_loader
   - [ ] `update_payment_status.py` - Use path_utils, data_loader

4. **Update validators** (2 scripts)
   - [ ] `validate_fleet_data.py` - Use path_utils, data_loader
   - [ ] `check_sail_limits.py` - Use path_utils, data_loader

5. **Update analysis** (1 script)
   - [ ] `analyze_sailmaker_trends.py` - Fix undefined variables, use utils

## 📋 Testing Phase

### Test Individual Scripts

```bash
cd /Users/chad/Projects/Fleet22_us

# Test scrapers
python -m scripts.scrapers.scrape_sail_tags
python -m scripts.scrapers.scrape_fleet_boats
python -m scripts.scrapers.scrape_owner_status

# Test processors
python -m scripts.processors.combine_data_sources
python -m scripts.processors.update_payment_status

# Test validators
python -m scripts.validators.validate_fleet_data
python -m scripts.validators.check_sail_limits

# Test analysis
python -m scripts.analysis.analyze_sailmaker_trends
```

### Expected Results
- [ ] No import errors
- [ ] Logs written to `logs/scraping.log`
- [ ] Data saved to correct paths in `data/` subdirectories
- [ ] Backups created for modified files

## 🔧 Configuration Updates

### Update GitHub Actions Workflow

If you have `.github/workflows/*.yml` files that run scripts:

1. Find workflow files
   ```bash
   find .github/workflows -name "*.yml"
   ```

2. Update script paths:
   - `python scraper/fleetBoats_github_actions.py` → `python -m scripts.scrapers.scrape_fleet_boats`
   - Update any hardcoded paths

3. Add requirements installation:
   ```yaml
   - name: Install dependencies
     run: |
       pip install -r scripts/requirements.txt
   ```

## 📦 Dependency Installation

```bash
cd scripts
pip install -r requirements.txt
```

### Verify Installation
```bash
pip list | grep -E "(beautifulsoup4|requests|pandas|matplotlib|tqdm)"
```

## 🗂️ Data Directory Verification

Ensure data subdirectories exist:

```bash
mkdir -p data/boats data/sails data/members data/races data/calendar data/payments logs
```

Or run from Python:
```bash
cd /Users/chad/Projects/Fleet22_us
python -c "from scripts.utils.path_utils import ensure_directories; ensure_directories()"
```

## 🧪 Quick Validation Tests

### Test 1: Path Utils
```bash
python -c "from scripts.utils.path_utils import *; print(f'Boats: {BOATS_FILE}'); print(f'Sails: {SAIL_TAGS_FILE}')"
```

### Test 2: Logger
```bash
python -c "from scripts.utils.logger import setup_logger; logger = setup_logger('test'); logger.info('Test message')"
cat logs/scraping.log | tail -1
```

### Test 3: Data Loader
```bash
python -c "from scripts.utils.data_loader import load_json; from scripts.utils.path_utils import SAIL_TAGS_FILE; data = load_json(SAIL_TAGS_FILE); print(f'Loaded {len(data)} records')"
```

## 🔀 Git Operations

### Review Changes
```bash
git status
git diff scripts/
```

### Stage Changes
```bash
git add scripts/
git add SCRIPTS_ANALYSIS.md
```

### Commit
```bash
git commit -m "refactor: Reorganize scripts with improved structure and utilities

- Renamed all scripts to snake_case for consistency
- Created modular structure: scrapers, processors, validators, analysis
- Added shared utilities: path_utils, logger, data_loader
- Updated requirements.txt with current dependency versions
- Added comprehensive documentation and __init__.py files

Closes #[issue-number] (if applicable)"
```

### Push
```bash
git push origin feature/rearrange
```

## 📊 Success Metrics

After completion, verify:
- [ ] All scripts run without errors
- [ ] Logs appear in `logs/scraping.log`
- [ ] Data files saved to correct locations
- [ ] No hardcoded paths in scripts
- [ ] Consistent logging format across all scripts
- [ ] Backups created automatically
- [ ] All tests pass

## 🚀 Future Enhancements (Optional)

- [ ] Add pytest tests for each module
- [ ] Create CLI interface with click
- [ ] Add configuration file (config.yaml)
- [ ] Set up pre-commit hooks for code formatting
- [ ] Add type hints throughout
- [ ] Create GitHub Actions workflow for testing
- [ ] Add error recovery and retry logic
- [ ] Create unified orchestration script

## 📞 Troubleshooting

### Common Issues

1. **Import errors**: Make sure to run from project root with `python -m scripts.scrapers.script_name`

2. **Path not found**: Run `path_utils.ensure_directories()` first

3. **Permission denied on logs**: Check directory permissions
   ```bash
   chmod -R 755 logs/
   ```

4. **Old data in cache**: Clear backups if testing
   ```bash
   find data -name "*_backup_*" -delete
   ```

## 📝 Notes

- Keep `scrape_fleet_boats_local.py` as backup/alternative to main scraper
- The `generators/` directory is empty and ready for future calendar generation scripts
- All utility modules are importable as packages: `from scripts.utils import logger`

---

**Current Priority**: Update imports in all scripts (start with update_imports.sh)
