# Fleet 22 — Coding Conventions & Rules

> **Last Updated:** 2026-03-10
> **Purpose:** Prevent repeated mistakes. Read this BEFORE modifying any code or data.

---

## Critical Rules (MUST follow)

### 1. Payment Data Preservation
**Fleet Dues are MANUALLY maintained. NEVER auto-overwrite them.**

When scraping or processing boat data:
- Extract new data from HTML
- Load existing `boats_fleet22.json`
- Merge: preserve `Fleet Dues` and `Class Dues` from existing data
- Only `Class Dues` may be auto-synced from membership data

### 2. Dues Format (Simplified)
The project uses the **simplified** dues format as of late 2025:
```json
"Fleet Dues": "Paid"       // or "Not Paid"
"Class Dues": "Not Paid"   // or "Paid"
```
- Values MUST be exactly `"Paid"` or `"Not Paid"` (case-sensitive)
- Do NOT use: `"Unpaid"`, `"Unknown"`, `"Yes"`, `"No"`, booleans
- Do NOT add year-specific fields like `"Fleet Dues 2026"`

### 3. Data Key Conventions
| File | Key Style | Example |
|------|-----------|---------|
| boats_fleet22.json | Title Case + spaces | `"Hull Number"`, `"Boat Name"` |
| j105_members_status.json | Title Case + special chars | `"Owners/Helmsmen"`, `"Certificate No."` |
| combined_fleet_data.json | snake_case | `"hull_number"`, `"boat_name"` |
| fleet22_active_roster.json | snake_case | `"hull_number"`, `"class_membership"` |

**Never mix key styles within the same file.**

### 4. Backup Before Write
Always create backups before modifying JSON data files. Use `data_loader.save_json()` which handles this automatically. Pattern: `<filename>_backup_YYYYMMDD_HHMMSS.json`

---

## Known Pitfalls

### Data Format Mismatch
Several scripts still reference the **legacy detailed format** (`"Fleet Dues 2025"`, `"Fleet Dues Payment Date"`):
- `scripts/processors/manage_boat_data.py` — `BOAT_SCHEMA` uses old field names
- `PAYMENT_DATA_PRESERVATION.md` — Documents the old format as the solution
- `FLEET_DUES_MANUAL.md` — Describes the old format

**If updating these scripts, align with the simplified format.**

### Yacht Club Data Gaps
Some boats have missing or placeholder yacht clubs:
- Hull 123 (Good Lookin): `""` (empty)
- Hull 10 (Zamboni): `""` (empty)
- Hull 327 (J-4): `"Tba"` (placeholder)

### Missing Owner/Contact Fields
The current simplified `boats_fleet22.json` does NOT include `Owner` or `Contact Email`. These fields are available in `j105_members_status.json` and `fleet22_active_roster.json`.

### HTML Navigation Consistency
All nav bars should show:
- "North Americans 2026" (not "2024")
- Link target: `north_americans_2024.html` (filename kept for URL stability)
- Copyright: `© 2026 Fleet 22 Lake Erie`

### CSS Files
- `assets/css/styles.css` — Main site styles
- `assets/css/na.css` — North Americans-specific styles

---

## File Modification Checklist

### Before Editing boats_fleet22.json
- [ ] Confirm using simplified format (`"Paid"` / `"Not Paid"`)
- [ ] Backup will be created automatically by `save_json()`
- [ ] Hull numbers are strings, not integers
- [ ] Do not add fields not in the current schema

### Before Editing HTML Pages
- [ ] Copyright year: 2026
- [ ] Nav link text: "North Americans 2026"
- [ ] Nav link href: `north_americans_2024.html` (unchanged filename)
- [ ] Check both desktop and mobile nav if applicable

### Before Editing Python Scripts
- [ ] Use `scripts/utils/path_utils.py` for all file paths
- [ ] Use `scripts/utils/data_loader.py` for JSON I/O
- [ ] Use `scripts/utils/logger.py` for logging
- [ ] Run from `scripts/` directory with `python -m module.name`
- [ ] Test locally before pushing (CI runs weekly)

---

## Git & Deployment Notes

- **Tracked data files:** `boats_fleet22.json`, `j105_members_status.json`, `sail_tags.json`
- **Gitignored:** `combined_fleet_data.json`, `fleet_statistics.json`, `logs/`, `__pycache__/`
- **CI bot commits as:** `github-actions[bot]`
- **Artifact retention:** 14 days
- **Never commit:** Credentials, `.env` files, `node_modules`
