# Fleet 22 — Coding Conventions & Rules

> **Last Updated:** 2026-10-21
> **Purpose:** Prevent repeated mistakes. Read this BEFORE modifying any code or data.

---

## Critical Rules (MUST follow)

### 1. Payment Data Preservation
**Fleet Dues are MANUALLY maintained. NEVER auto-overwrite them.**

When scraping or processing boat data:
- Build fleet boats from freshly fetched class membership records
- Load existing `boats_fleet22.json`
- Merge: preserve `Fleet Dues` and `Yacht Club` from existing data
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
Always create backups before modifying JSON data files. Use `data_loader.save_json()` which handles this automatically. Pattern: `<filename>_backup_YYYYMMDD_HHMMSS_microseconds.json`

---

## Known Pitfalls

### Shared Membership and Payment Rules
Use `utils/membership.py`: only a current-calendar-year full `Member` satisfies Class Dues, considering all co-owner records. Associate membership alone does not. Do not infer Fleet Dues from class membership.

The boat manager and CSV tracker use the simplified boat schema. CSV details stay in a current-season `Paid YYYY` column; importing YES rows preserves existing paid statuses for NO/blank rows. Historical guides have been replaced with current commands.

### Yacht Club Data Gaps
Some boats have missing or placeholder yacht clubs:
- Hull 123 (Good Lookin): `""` (empty)
- Hull 10 (Zamboni): `""` (empty)
- Hull 327 (J-4): `"Tba"` (placeholder)

### Missing Owner/Contact Fields
The current simplified `boats_fleet22.json` does NOT include `Owner` or `Contact Email`. These fields are available in `j105_members_status.json` and `fleet22_active_roster.json`.

### HTML Navigation Consistency
All shared nav bars should show:
- A Members dropdown containing Members Overview, Sail Declaration, Fleet Dues, and Dues Status. Fleet Dues is not a separate top-level navigation item.
- The Members hub uses `member-resources`, `sail-declaration`, and `fleet-dues` anchors; preserve these links.
- "Event Archive" linking to `pages/events_archive.html` with the appropriate relative path
- North Americans 2026 is completed; preserve `north_americans_2024.html` and its `current-event` / `historical-event` anchors for archived links
- Copyright: `© 2026 Fleet 22 Lake Erie`

### Sail Declaration
- Interactive and printable forms use generic J/105 branding; no fixed event year or championship logo.
- Optional event name and dates are saved/printed. Keep lookup suggestions and manual overrides working.
- Event details stay when switching boats. Storage remains the most recent declaration per hull.

### Shared Boat/Owner Lookup
- Declaration and sail analysis extend `BoatLookupController` in `assets/js/boat-lookup.js`; do not duplicate the registry matching or suggestion logic.
- Load the shared script before the page application script and include `assets/css/boat-lookup.css`.
- In analysis, names are search queries. Only explicit suggestion/hull selection changes the chart; always keep selected identity and results in sync.
- Missing registry matches must not block direct hull analysis. Clear old charts/statistics for boats without sail records.

### Sail Analysis Records and Filters
- Chart totals count source registration records, not unique certificates or current sail inventory. Preserve repeated certificates and flag same-hull/cross-hull occurrences; do not silently deduplicate transfers.
- Validate full calendar dates without timezone conversion or rollover. Unknown dates remain available in the table and never create a chart year.
- Year/type/maker filters affect chart and table; table search and selected-cell scope affect only the table. Recent presets use the current calendar year and exclude undated records unless explicitly re-enabled.
- Keep cell activation usable by click, tap, Enter and Space. Render source fields as text, keep mobile scrolling inside chart/table containers, and prevent hover tooltips from expanding the mobile viewport.

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
- Edit shared navigation/footer in `templates/`, then run `python -m scripts.generate_site`
- Run `python -m scripts.generate_site --check` and `python -m scripts.validators.check_site`
- [ ] Copyright year: 2026
- [ ] Nav link text: "Event Archive"
- [ ] Nav link href: relative path to `pages/events_archive.html`
- [ ] Check both desktop and mobile nav if applicable

### Before Editing Python Scripts
- [ ] Use `scripts/utils/path_utils.py` for all file paths
- [ ] Use `scripts/utils/data_loader.py` for JSON I/O
- [ ] Use `scripts/utils/logger.py` for logging
- [ ] Run from `scripts/` directory with `python -m module.name`
- [ ] Test locally before pushing (CI runs weekly)

---

## Git & Deployment Notes

- **Tracked data files:** source snapshots, `data/combined/*.json`, and `data/metadata.json`
- **Gitignored:** backups, payment tracker CSVs, logs, bytecode and browser artifacts
- **CI bot commits as:** `github-actions[bot]`
- **Artifact retention:** 14 days
- **Never commit:** Credentials, `.env` files, `node_modules`
