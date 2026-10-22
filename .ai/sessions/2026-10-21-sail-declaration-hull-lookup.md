## Session: 2026-10-21 — Sail declaration hull lookup and manual overrides

**Agent:** Codex

### What Was Done
- Connected the interactive sail declaration's hull input to deployment-local class membership and Fleet 22 boat snapshots.
- Preferred owner records and current/recent membership over crew or historical owners; equally recent co-owners are included together. Removed the historical sail-purchaser fallback.
- Kept owner and boat name editable with inline status and a Use registry details reset button. Delayed lookups preserve manual edits. Missing matches and network failures allow manual entry.
- Fixed Save/Load ordering to preserve edited owner/boat names, including blank values, and sail selections. Normalized hull matching/storage, cleared stale boat contact/color details on hull changes, and escaped dynamic printed values.
- Added 11 focused Node tests to CI and updated the declaration documentation.

### Validation
- All 11 Node tests and the existing 22 Python tests pass.
- Shared-template, local-site resource/link checks, JavaScript syntax and git whitespace checks pass.
- Browser verified hull 493 → Rapscallion / Tom Cliffel; hull 124 prefers Matthew Arno over an old owner record.
- Browser verified manual overrides through Save/Load and captured print HTML, registry reset, unknown hulls, failed membership requests with sails still usable, and delayed responses after manual edits.
- Inspected the mobile form; no horizontal document overflow at 390px.

### Key Decisions
- Changes apply to the interactive `Sail_dec_auto.html` form linked from Members. The static printable declaration is unchanged.
- Owner and boat edits affect the saved declaration only; registry data is never modified.
- Existing event branding/year remains unchanged as outside this request.

### Files Changed
- `tools/documents/sail_declaration.js`: lookup, override state, persistence and print escaping.
- `tools/documents/Sail_dec_auto.html`: lookup status, input hints and registry-reset button.
- `tests/test_sail_declaration.cjs`: focused regressions.
- `.github/workflows/run-python-scripts.yml`: Node test step.
- `tools/documents/SAIL_DECLARATION_README.md`: usage and lookup rules.
- This session summary.

### Follow-up
- Changes are local; no commit, push or deployment performed.
