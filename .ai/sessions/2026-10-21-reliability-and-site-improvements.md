## Session: 2026-10-21 — Data reliability and website improvements

**Agent:** Codex

### What Was Done
- Replaced independent scraper CI jobs with offline checks and a main-only staged updater. Membership refresh precedes fleet building. The updater verifies source files have not changed locally before publication.
- Added shared membership/co-owner rules, full-record schema validation, record/hull drop detection, empty-extraction failures, bounded HTTPS retries/timeouts, atomic JSON replacement and original-byte backups.
- Aligned the manual boat manager, season CSV tracker and follow-up reports with simplified Fleet Dues. Corrected converter preservation and season-reset backups.
- Corrected current-owner precedence, current full-membership statistics and historical sail fleet attribution; refreshed source and combined data successfully.
- Added successful-refresh metadata with file hashes. Member/dues tables and sail tools load deployment-local data, with text-only table rendering and visible load errors.
- Added shared static navigation/footer templates, sitemap generation and a local HTML/CSS/anchor/resource checker. Fixed public and tool paths, mobile menu behavior, table overflow and sponsor image overflow.
- Pinned public-page Bootstrap 5.3.8 with integrity hashes, added responsive hero sources, removed unreferenced duplicate photos and the stale duplicate treemap dataset, and removed tracked bytecode.
- Split optional plotting dependencies from the minimal CI toolset and added a Python 3.10-compatible scraping lockfile. Updated current guides and project memory.

### Validation
- 22 standard-library offline regression tests pass in Python 3.11.
- Full source validation, generated-fragment drift check, local website link/resource/anchor/sitemap checks, shell syntax, JavaScript syntax, dependency consistency and git whitespace checks pass.
- Exact lockfile resolves for Python 3.10. The initial Python 3.11 freeze selected SoupSieve 3, which requires 3.11.5; capped it below 3 and verified the compatible lock.
- A live staged registry refresh succeeded: 836 membership records, 8,336 sail records, 22 local fleet boats. All 22 manual Fleet Dues values are unchanged.
- Existing user edits to both 2026 payment-sync report files are byte-for-byte unchanged.
- Browser checks covered eight public pages on desktop/mobile, all public mobile menus, document overflow, live table rows/freshness, failed HTTP responses and injected HTML rendered as literal text. Public pages have no document overflow at 390px; dues table scrolls within its container.
- Inspected desktop homepage and mobile dues screenshots. Forced stylesheet revalidation to avoid stale browser-cache results when verifying status colors.

### Key Decisions
- Preserve the fleet builder's existing full-Member-only class-dues rule; any current-year full co-owner membership satisfies it. Associate membership alone does not.
- Retain historical public `/images/` and North Americans page URLs.
- Keep source and derived JSON tracked. Normal updates leave manually edited payment reports alone; explicit payment-sync commands regenerate them.
- Git remote is actually `dailypush/Fleet22`; the earlier review's repository-name warning was corrected. Relative data URLs improve deployment portability.

### Limits and Follow-up
- Files remain local; no commit, push or deployment was performed.
- JSON replacement is atomic per file. Validation happens before publication, but disk failures during the publication sequence can leave a mixed snapshot; original-file backups support recovery.
- External link auditing, Lighthouse and screen-reader audits were not performed.

### Primary Files Changed
- `.github/workflows/run-python-scripts.yml`, `scripts/update_all_data.py`, shared `scripts/utils/`, processors, scrapers, reports, validators and `tests/test_data_pipeline.py`.
- `templates/`, `scripts/generate_site.py`, `assets/js/boats-table.js`, public HTML, tool resource URLs, CSS, sitemap and current data snapshots.
- Root README/payment guides, scripts README and `.ai/` project knowledge/conventions.
