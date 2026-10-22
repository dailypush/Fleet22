# Fleet 22 Lake Erie

Static website and Python data tools for Fleet 22 of the J/105 class.
The site is served by GitHub Pages at https://fleet22.us.

## Local setup

Use Python 3.10 or newer. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements-scraping.lock
python -m unittest discover -s tests -v
python -m scripts.validators.validate_fleet_data
python -m scripts.validators.check_site
python -m http.server 8000 --bind 127.0.0.1
```

For plotting and sail-limit analysis, install the full toolset:

```bash
pip install -r scripts/requirements.txt
```

## Refreshing fleet data

```bash
./scripts/update_all_data.sh
# Or, with the intended Python interpreter active:
python -m scripts.update_all_data
```

The refresh runs in a temporary data directory:

1. Fetch current class membership and sail tags with HTTPS verification, bounded timeouts and retries.
2. Build the Fleet 22 roster from the freshly fetched membership, considering all co-owner records.
3. Validate every record and reject empty datasets, malformed rows, duplicate boat hulls, invalid dues values, or drops exceeding 20% in record count or existing hull coverage.
4. Generate combined data and statistics. Current membership owners take precedence over historical sail purchasers; the local fleet registry supplies Fleet 22 boat names.
5. Publish validated files using atomic replacement and timestamped backups. Publish `data/metadata.json` last with the successful check time, record counts and file hashes.

A scrape or processing failure leaves the published snapshots unchanged. Local source edits made while the refresh runs also stop publication. Backups have microsecond timestamps and are ignored by Git.

If a legitimate registry change exceeds the drop threshold, inspect the removed records and deliberately update the baseline roster before rerunning. A paid boat is never automatically removed from the local roster; reconcile its membership manually first.

## Dues rules

`data/boats/boats_fleet22.json` uses exactly these fields:

```json
{
  "Hull Number": "493",
  "Boat Name": "Rapscallion",
  "Yacht Club": "EYC",
  "Fleet Dues": "Paid",
  "Class Dues": "Not Paid"
}
```

- **Fleet Dues are manually maintained.** Automated refreshes preserve them and yacht clubs by hull number.
- **Class Dues** are paid when any co-owner has `Member YYYY` for the current calendar year. Associate membership alone, previous seasons and future seasons do not satisfy this rule.
- Boat JSON uses `Paid` / `Not Paid`. Season-specific dates, payment methods and amounts belong in the ignored payment tracker CSV.
- A manual correction requires an explicit `--paid` or `--not-paid` argument:

```bash
python -m scripts.processors.manage_boat_data update --hull 493 --paid
python -m scripts.processors.manage_boat_data report
python -m scripts.reports.payment_tracker create
python -m scripts.reports.payment_tracker update --hull 493 --paid --method Venmo
python -m scripts.processors.manage_boat_data merge
python -m scripts.reports.generate_payment_followup
```

CSV columns use `Paid YYYY` for the current season. Creating an existing tracker fails to protect recorded payments. Importing a tracker only applies YES payments; NO/blank entries preserve existing manual payments. Old-season CSV files must be migrated deliberately rather than silently imported.

See [the dues manual](FLEET_DUES_MANUAL.md) for resets and migration.

## Website maintenance

Edit page content directly in `index.html` and `pages/`. Shared navigation and footers come from `templates/`:

```bash
python -m scripts.generate_site
python -m scripts.generate_site --check
python -m scripts.validators.check_site
```

Generated HTML stays checked in, so hosting requires no build. The generator updates the sitemap with real page paths and pins public-page Bootstrap CSS/JS to the same version with integrity hashes. Navigation links to `pages/events_archive.html`. The North Americans history retains its existing `pages/north_americans_2024.html` URL and section anchors for stability.

Members is the hub for Sail Declaration, Fleet Dues payment instructions (`pages/members.html#fleet-dues`), and Dues Status. The shared Members dropdown links to these resources; the existing declaration/status URLs remain stable.

The sail declaration is reusable across J/105 events, with optional event name/dates saved and printed alongside boat and sail information.

Sail analysis (`analysis/sail_analysis_heatmap.html`) uses the same boat/owner suggestions as the declaration. Type two characters and choose a match to update the hull, names, chart and statistics together, or select a hull directly. Typing alone leaves the selected analysis unchanged. Missing registry data does not block hull analysis; boats without sail records show an empty state.

Filter registrations by delivery-year range, sail type and sailmaker, with calendar-year shortcuts for the last three/five years. Unknown delivery dates can be included in the table independently of the year range; they never appear on the chart. Selecting a numbered chart cell by click, tap, Enter or Space opens its source records. The searchable table includes certificates, historical purchasers, notes and record flags, with 25 rows per page. Table search does not change chart totals. Switching hulls resets filters and table search.

Counts represent source registration records, not current inventory or unique sails. Repeated certificates are retained and flagged, including cross-hull occurrences that may reflect transfers. Notes flags are keyword hints, not class-rule exemption decisions. The chart includes empty years, sizes itself by unique rows, and shows a numeric color-scale maximum for the current filters.

Both tools share current-owner matching and accessible suggestions in `assets/js/boat-lookup.js` and `assets/css/boat-lookup.css`. Run the JavaScript regressions with `node --test tests/test_*.cjs`.

Members, dues and sail analysis load deployment-local JSON. The dues page displays successful refresh time from `data/metadata.json`; failed data loads show an error. Keep historical event content dated and avoid labeling past events as upcoming.

The checker verifies local HTML resources, CSS image URLs, fragment targets and sitemap paths across public pages, analysis pages and tools. External links require separate review.

## Automation

`.github/workflows/run-python-scripts.yml` runs offline regression, data, template and link checks on pushes and pull requests. Scheduled Monday-midnight UTC and manual runs refresh the sources. Only main-branch non-PR runs can commit generated snapshots; other jobs have read-only permissions. Concurrency groups prevent overlapping runs for the same ref. Refresh logs and generated data are retained as workflow artifacts for 14 days.

## Data and tools

- `data/boats/`: local fleet registry and manual dues.
- `data/members/`, `data/sails/`: scraped source snapshots.
- `data/combined/`: tracked combined dataset and statistics, regenerated by updates.
- `data/payments/`: manually managed reports and ignored tracker CSVs.
- `analysis/`: browser visualizations; `scripts/analysis/` and `analysis/heatmaps/`: Python plots.
- `tools/documents/`: printable event forms and sailing tools.
- `images/`: original public photo URLs; assets and branding live under `assets/`.

## License

See [LICENSE](LICENSE).
