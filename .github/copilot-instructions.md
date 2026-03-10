# GitHub Copilot Instructions — Fleet 22 Lake Erie

## Project Context
This is the Fleet 22 J/105 sailing club website (https://fleet22.us) with Python backend scripts for data management. Fleet 22 is based on Lake Erie, Cleveland OH area.

## Before Any Work
Read these files for full context:
- `.ai/CODEBASE_KNOWLEDGE.md` — Architecture, data schemas, script inventory
- `.ai/CONVENTIONS.md` — Critical rules, known pitfalls, checklists
- Recent files in `.ai/sessions/` — Past session learnings

## Critical Rules

### Data Files
- `boats_fleet22.json` uses simplified format: `"Fleet Dues": "Paid"` or `"Not Paid"`
- **Never auto-overwrite Fleet Dues** — they are manually maintained
- Class Dues may be auto-synced from membership data
- Always back up before writing (use `scripts/utils/data_loader.py`)
- Key style: Title Case with spaces in source files, snake_case in combined data

### Python Scripts
- Run from `scripts/` directory with `python -m module.name`
- Use `scripts/utils/path_utils.py` for paths, `data_loader.py` for JSON I/O, `logger.py` for logging
- Python 3.10+

### HTML Pages
- Copyright: `© 2026 Fleet 22 Lake Erie`
- Navigation: "North Americans 2026" (links to `north_americans_2024.html` — kept for URL stability)
- Check both desktop and mobile nav when editing

## After Each Session
Create a session summary at `.ai/sessions/YYYY-MM-DD-<topic>.md` using the template at `.ai/sessions/SESSION_TEMPLATE.md`. Capture: what was done, failed approaches, mistakes, patterns discovered, and open issues.
