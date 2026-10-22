# Fleet 22 — Codebase Knowledge Base

> **Last Updated:** 2026-10-21
> **Maintained by:** AI agents across sessions

---

## 1. Project Overview

**Fleet 22 Lake Erie** is the official website and data management platform for Fleet 22 of the J/105 Class Sailing Association, based in the Cleveland, Ohio / Lake Erie area.

- **Domain:** https://fleet22.us (GitHub Pages + custom CNAME)
- **Repository:** `dailypush/Fleet22_us` (MIT License)
- **Two components:** Static HTML website + Python backend scripts

### Fleet Details
- ~22 boats in Fleet 22, ~662 total in J/105 class worldwide
- Annual fleet dues: **$150/boat**
- Payment methods: Venmo (@fleet22lakerie), Check, Online, Cash
- Yacht clubs: EYC (7 boats), BHSC (4), NCYC (3), BYC (2), SSC (1), GRSC (1)

---

## 2. Data Architecture

### Primary Data Files

| File | Records | Description |
|------|---------|-------------|
| `data/boats/boats_fleet22.json` | ~22 | Fleet 22 boat registry + dues status |
| `data/members/j105_members_status.json` | ~836 | Full J/105 class membership roster |
| `data/sails/sail_tags.json` | ~8,336 | Sail certification records (all fleets) |
| `data/combined/combined_fleet_data.json` | ~662 | Tracked unified dataset |
| `data/fleet22_active_roster.json` | ~18 | Active Fleet 22 roster with owners |

### Schema: boats_fleet22.json (CURRENT — Simplified Format)
```json
{
    "Hull Number": "493",       // String — unique boat ID
    "Boat Name": "Rapscallion", // String
    "Yacht Club": "EYC",        // String abbreviation (BYC, BHSC, EYC, NCYC, SSC, GRSC, "", "Tba")
    "Fleet Dues": "Paid",       // EXACTLY "Paid" or "Not Paid" (case-sensitive)
    "Class Dues": "Not Paid"    // EXACTLY "Paid" or "Not Paid" (case-sensitive)
}
```

### Schema: j105_members_status.json
```json
{
    "Hull": "5",
    "Owners/Helmsmen": "Richard Stearns",
    "Status": "OW",
    "Boat Name": "Glider IV",
    "Location": "Illinois",
    "Fleet": "5",                         // "22" = Fleet 22, "0" = unaffiliated
    "Class Membership": "Member 2026"     // "Member YYYY" | "Associate YYYY" | "" (lapsed)
}
```

### Schema: sail_tags.json
```json
{
    "Hull": "7",
    "Purchaser": "Don Aakhus",
    "Certificate No.": "1110347U",
    "Sailmaker": "Ullman",               // North, Quantum, Ullman, Doyle, etc.
    "Delivery Date": "2011-12-22",       // YYYY-MM-DD
    "Sail Type": "M",                    // M (Main), J (Jib), S89 (Spinnaker 89), S77 (Spinnaker 77)
    "Fleet": "0",
    "Notes": ""
}
```

### Schema: combined_fleet_data.json (snake_case keys!)
```json
{
    "hull_number": "10",
    "owner": "Mike Aiello",
    "boat_name": "Zamboni",
    "fleet": "22",
    "class_membership": "",
    "sail_tags": [
        { "certificate": "1003024U", "sailmaker": "Ullman", "delivery_date": "2010-06-02", "type": "J" }
    ]
}
```

**⚠ IMPORTANT:** Combined data uses **snake_case** keys. Source files use **Title Case with spaces**.

---

## 3. Scripts Architecture

**Root:** `scripts/` — Run with `python -m scripts.module.name` from the repository root
**Python:** 3.10+ | **~2,900 lines** across 18 files

### Scrapers (`scripts/scrapers/`)
| Script | Source | Output |
|--------|--------|--------|
| `scrape_sail_tags.py` | archive.j105.org sail tag list | sail_tags.json |
| `scrape_owner_status.py` | archive.j105.org owners page | j105_members_status.json |
| `scrape_fleet_boats.py` | Fresh members JSON, filtered to Fleet 22 | boats_fleet22.json |
| `extract_world_sailing_numbers.py` | Race results CSV | — |

### Processors (`scripts/processors/`)
| Script | Purpose |
|--------|---------|
| `combine_data_sources.py` | Combines boats + members + sails → combined data |
| `update_payment_status.py` | Syncs Class Dues from membership data |
| `manage_boat_data.py` | CLI: `enhance`, `update`, `merge`, `report` |

### Reports (`scripts/reports/`)
| Script | Purpose |
|--------|---------|
| `payment_tracker.py` | CLI: `create`, `update`, `summary` (CSV-based) |
| `generate_payment_followup.py` | Follow-up reports grouped by yacht club |

### Validators (`scripts/validators/`)
| Script | Purpose |
|--------|---------|
| `validate_fleet_data.py` | JSON structure/integrity validation |
| `check_sail_limits.py` | J/105 sail purchase limit compliance |

### Utilities (`scripts/utils/`)
| Script | Purpose |
|--------|---------|
| `path_utils.py` | Centralized path constants (PROJECT_ROOT, DATA_DIR, etc.) |
| `data_loader.py` | `load_json()` / `save_json()` with auto-backup |
| `logger.py` | Logging config → `logs/scraping.log` + console |
| `reset_dues_season.py` | Resets all dues to "Not Paid" for new season |
| `simplify_dues_format.py` | Converts detailed → simplified dues format |

### Shell Scripts
- `scripts/update_all_data.sh` — Master script to run all scrapers + processors
- `scripts/update_imports.sh` — Helper for import path updates

---

## 4. CI/CD Pipeline

**File:** `.github/workflows/run-python-scripts.yml`

**Triggers:** Main push, PR, weekly Monday midnight UTC, manual dispatch.

**Jobs:** `checks` runs offline unit tests, source validation, shared-template drift checks and local site-link checks. Only non-PR main runs execute `update-data` with write permissions; concurrency groups prevent overlapping same-ref runs.

The staged updater (`scripts/update_all_data.py`) refreshes membership and sails, builds boats from fresh membership, validates all sources, generates combined data, then publishes with backups and individual atomic replacements. An empty parse, suspicious >20% drop, corrupt baseline, removed paid boat or concurrent local source edit prevents publication. `metadata.json` records successful live check time and published file hashes. Disk failures during publication can interrupt the sequence of individual replacements; backups allow recovery.

**Commit behavior:** Tracks all three source snapshots, combined data/statistics and freshness metadata. Normal registry updates preserve manual Fleet Dues and payment reports.

**Dependencies:** CI uses `requirements-scraping.lock`; optional plotting dependencies are separate. Run `python -m unittest discover -s tests -v` for offline regressions.

---

## 5. Website Pages

| Page | Path | Purpose |
|------|------|---------|
| Home | `index.html` | Landing page with SEO (Schema.org, OG, Twitter) |
| Members | `pages/members.html` | Member resource hub, dues instructions, fleet boat list |
| Dues Status | `pages/fleetdues.html` | Members subpage; fetches local JSON + freshness metadata |
| Classifieds | `pages/classifieds.html` | Boat/equipment listings |
| Join | `pages/join.html` | Fleet 22 membership info |
| Media Kit | `pages/media_kit.html` | NA 2024 media/sponsor kit |
| Event Archive | `pages/events_archive.html` | Past championship and race-week links by year |
| North Americans | `pages/north_americans_2024.html` | Archived Seattle 2026 and Cleveland 2024 championships |
| Race Week News | `pages/news/cleveland-race-week-2024-highlights.html` | 2024 CRW recap |

The homepage has an end-of-2026-season wrap-up and 2027 planning message. The 2026 North Americans are archived; registration prompts are removed. Shared navigation points to Event Archive. Existing championship URLs/section anchors remain valid.

Members is the primary entry point for Sail Declaration, Fleet Dues payment instructions, and Dues Status. The shared Members dropdown links to all three. Member-resource cards use `member-resources`, `sail-declaration`, and `fleet-dues` anchors. Declaration and status page URLs remain unchanged and include links back to Members. Homepage/archive resource links lead through the Members hub. `assets/js/navigation.js` closes the mobile menu on destination selection; member-section anchors have spacing below the sticky navbar.

`tools/documents/Sail_dec_auto.html` is a generic J/105 sail declaration with optional event name/dates, hull/name/owner lookup suggestions and editable overrides. Event details persist across boat changes and Save/Load and appear in print; storage is still the latest declaration per hull. `Sail_declaration.html` is the generic blank printable counterpart. Run `node --test tests/test_sail_declaration.cjs` for focused regressions.

### Analysis/Visualization Pages
- `analysis/githeatmap.html` — Git commit activity
- `analysis/heatmap.html` — Sail purchase heatmap
- `analysis/sail_analysis_heatmap.html` — Hull/boat/owner search and sail purchase heatmap
- `analysis/treemap/treemap.html` — Sail tag treemap

Sail analysis and declaration share `assets/js/boat-lookup.js` (`BoatLookupController`) and `assets/css/boat-lookup.css`. This centralizes current-owner/co-owner ranking, partial name matching, registry loading and accessible suggestions. Analysis name inputs are searches: explicit selection updates hull, names, chart and statistics; typing alone preserves the selected hull. Direct hull selection remains usable if membership lookup fails. The selector includes registry boats without sails and shows a cleared no-data state for them. Mobile charts scroll within their container. JavaScript tests run via `node --test tests/test_*.cjs` in CI.

Shared public navigation/footer come from `templates/` via `python -m scripts.generate_site`. Generated HTML and sitemap stay checked in. Public pages use pinned Bootstrap 5.3.8 with integrity hashes. Analysis pages load shared deployment-local sail data; the duplicate treemap dataset and unused duplicate photos were removed. Original `/images/` URLs remain valid.

---

## 6. File Naming & Backup Conventions

- **Backups:** Auto-created before writes: `<filename>_backup_YYYYMMDD_HHMMSS_microseconds.json`
- **Logs:** `logs/scraping.log`, `logs/data_management.log`, `logs/reports.log`
- **Log format:** `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`
- **Payment reports:** `data/payments/payment_sync_report_YYYY.txt`, `payment_sync_summary_YYYY.txt`

---

## 7. SEO & Deployment

- Custom domain via `CNAME` file
- `robots.txt` blocks: `/data/`, `/scraper/`, logs, test pages
- `sitemap.xml` maps 10 public URLs
- Schema.org SportsOrganization markup on homepage
- Open Graph + Twitter Card meta tags on all public pages
