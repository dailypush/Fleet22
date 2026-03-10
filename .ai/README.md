# AI Agent Memory System — Fleet 22 Lake Erie

This directory contains structured knowledge and session summaries for AI agents (GitHub Copilot, Cursor, Claude, etc.) working on the Fleet22_us project.

## Directory Structure

```
.ai/
├── README.md                    ← You are here
├── CODEBASE_KNOWLEDGE.md        ← Persistent project knowledge base
├── CONVENTIONS.md               ← Coding conventions and rules
└── sessions/
    ├── SESSION_TEMPLATE.md      ← Template for new session summaries
    └── YYYY-MM-DD-<topic>.md    ← Individual session summaries
```

## How AI Agents Should Use This System

### At Session Start
1. Read `CODEBASE_KNOWLEDGE.md` for project architecture and data formats
2. Read `CONVENTIONS.md` for coding rules and known pitfalls
3. Scan recent session files in `sessions/` for context on recent work

### During a Session
- Reference `CONVENTIONS.md` before making changes to data files or scripts
- Check if the task overlaps with issues documented in past sessions

### At Session End
Create a session summary using `SESSION_TEMPLATE.md`:
```
sessions/YYYY-MM-DD-<brief-topic>.md
```

## Quick Reference

| Question | Answer |
|----------|--------|
| What is this project? | Fleet 22 J/105 sailing club website + data management |
| Where is the website? | https://fleet22.us |
| How many boats? | ~22 in Fleet 22, 661 total in J/105 class |
| Annual dues? | $150 per boat |
| Python version? | 3.10+ |
| CI/CD? | GitHub Actions, weekly Monday midnight UTC |
| Data format? | Simplified: `"Paid"` / `"Not Paid"` |
