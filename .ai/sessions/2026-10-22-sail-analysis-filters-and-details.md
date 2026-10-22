## Session: 2026-10-22 — Sail analysis filters, records and chart improvements

**Agent:** Codex

### What Was Done
- Implemented the recommended first batch: accuracy/labels, delivery-year/type/maker filters, chart-cell drill-down and searchable records, and heatmap layout corrections.
- Validate complete calendar dates without local timezone conversion or date rollover. Unknown dates stay inspectable in the table and never become a `NaN` chart year.
- Preserve every source registration, flag repeated certificates on the same/across hulls, and distinguish record totals from current inventory. Replacement/used/transfer note flags are keyword hints only.
- Added inclusive year selectors, last-three/five-calendar-year presets, and an explicit include-undated checkbox. Switching hulls resets filters/search; year endpoints stay ordered.
- Added an accessible 25-row paginated table with certificate, date, type, maker, historical purchaser, notes and flags. Table search and selected chart cells scope only the table.
- Numbered cells activate by click, touch, Enter or Space and focus the details heading. Filters clear cell scope; resize preserves it.
- Heatmap height depends on unique rows, the timeline includes empty years, and the legend shows the current numeric maximum. Short timelines fit mobile; longer charts/table scroll inside their containers.
- Fixed a hover tooltip that could expand a mobile viewport after tapping; touch devices use the cell details and desktop tooltips stay within the viewport.
- Updated README, codebase knowledge and conventions.

### Validation
- All 42 JavaScript tests pass (21 analysis, 21 declaration), including full-snapshot count reconciliation, dates, filters, repeats/transfers, cell scope, text-safe rendering and pagination.
- All 22 Python regressions pass; shared-template drift, local site links/resources/anchors/sitemap, JavaScript syntax and whitespace checks pass.
- Browser checked real hulls 493, 649, 218 and 65 for combined filters, no matches, undated records, repeats/transfers, historical purchaser labels, pagination and cell details.
- Browser checked year endpoint correction, include-undated toggle, Enter/Space, name lookup, cleared selection, registry boats without sails, resize selection, unknown-date-only source data and unavailable membership lookup.
- Inspected desktop/mobile screenshots. Touch at 390px opens cell details; the document remains 390px wide, recent timelines fit, and long timelines scroll internally. No application errors in the simulated data/failure checks.

### Decisions and Follow-up
- Source data is unchanged. Duplicate certificate numbers are not silently removed: the current snapshot includes real transfers and same-hull repeated entries.
- The first batch does not add boat comparison, exports/share URLs, latest-sail summaries or declaration linking.
- Changes remain local and uncommitted; no push/deployment performed.

### Files Changed
- `analysis/sail-analysis.js`, `analysis/sail_analysis_heatmap.html`
- `tests/test_sail_analysis.cjs`
- `README.md`, `.ai/CODEBASE_KNOWLEDGE.md`, `.ai/CONVENTIONS.md`, this session record
