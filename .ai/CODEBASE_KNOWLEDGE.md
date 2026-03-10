# Fleet 22 — Codebase Knowledge Base

> **Last Updated:** 2026-03-10
> **Maintained by:** AI agents across sessions

---

## 1. Project Overview

**Fleet 22 Lake Erie** is the official website and data management platform for Fleet 22 of the J/105 Class Sailing Association, based in the Cleveland, Ohio / Lake Erie area.

- **Domain:** https://fleet22.us (GitHub Pages + custom CNAME)
- **Repository:** `dailypush/Fleet22_us` (MIT License)
- **Two components:** Static HTML website + Python backend scripts

### Fleet Details
- ~22 boats in Fleet 22, ~661 total in J/105 class worldwide
- Annual fleet dues: **$150/boat**
- Payment methods: Venmo (@fleet22lakerie), Check, Online, Cash
- Yacht clubs: EYC (7 boats), BHSC (4), NCYC (3), BYC (2), SSC (1), GRSC (1)

---

## 2. Data Architecture

### Primary Data Files

| File | Records | Description |
|------|---------|-------------|
| `data/boats/boats_fleet22.json` | ~22 | Fleet 22 boat registry + dues status |
| `data/members/j105_members_status.json` | ~900+ | Full J/105 class membership roster |
| `data/sails/sail_tags.json` | ~8,091 | Sail certification records (all fleets) |
| `data/combined/combined_fleet_data.json` | ~661 | Unified dataset (gitignored, CI artifact) |
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

**Root:** `scripts/` — Run with `python -m module.name` from `scripts/` directory
**Python:** 3.10+ | **~2,900 lines** across 18 files

### Scrapers (`scripts/scrapers/`)
| Script | Source | Output |
|--------|--------|--------|
| `scrape_sail_tags.py` | archive.j105.org sail tag list | sail_tags.json |
| `scrape_owner_status.py` | archive.j105.org owners page | j105_members_status.json |
| `scrape_fleet_boats.py` | pages/members.html (GitHub) | boats_fleet22.json |
| `scrape_fleet_boats_local.py` | pages/members.html (local) | boats_fleet22.json |
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

**File:** `.github/workflows/run-python-scripts.yml` (419 lines)

**Triggers:** Push to main, PRs to main, weekly cron (Monday midnight UTC), manual dispatch

**Jobs (4):**
1. `fetch-sail-tags` → Scrapes sail data
2. `fetch-owners-status` → Scrapes member data
3. `fetch-fleet-boats` → Scrapes fleet boat data (preserves payment fields!)
4. `process-and-commit` → Download artifacts → validate → combine → commit & push

**Commit behavior:** Only commits tracked files: `boats_fleet22.json`, `j105_members_status.json`, `sail_tags.json`. Combined data is artifact-only (gitignored).

---

## 5. Website Pages

| Page | Path | Purpose |
|------|------|---------|
| Home | `index.html` | Landing page with SEO (Schema.org, OG, Twitter) |
| Members | `pages/members.html` | Fleet 22 boat list (scraped by scripts) |
| Fleet Dues | `pages/fleetdues.html` | Payment status (fetches JSON from GitHub API) |
| Classifieds | `pages/classifieds.html` | Boat/equipment listings |
| Join | `pages/join.html` | Fleet 22 membership info |
| Media Kit | `pages/media_kit.html` | NA 2024 media/sponsor kit |
| North Americans | `pages/north_americans_2024.html` | NA 2026 Seattle Championship info |
| Race Week News | `pages/news/cleveland-race-week-2024-highlights.html` | 2024 CRW recap |

### Analysis/Visualization Pages
- `analysis/githeatmap.html` — Git commit activity
- `analysis/heatmap.html` — Sail purchase heatmap
- `analysis/sail_analysis_heatmap.html` — Comprehensive sail analysis
- `analysis/treemap/treemap.html` — Sail tag treemap

---

## 6. File Naming & Backup Conventions

- **Backups:** Auto-created before writes: `<filename>_backup_YYYYMMDD_HHMMSS.json`
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
