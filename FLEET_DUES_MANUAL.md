# Fleet Dues Manual Management Guide

## Overview
Fleet Dues (Fleet 22 Dues) are manually maintained in `boats_fleet22.json`. This gives you direct control over payment tracking without requiring external CSV files.

## Payment Fields in boats_fleet22.json

Each boat entry has the following Fleet Dues fields:
```json
{
  "Hull Number": "144",
  "Boat Name": "Fall Line",
  "Fleet Dues 2025": "Paid",
  "Fleet Dues Payment Date": "2025-09-15",
  "Fleet Dues Payment Method": "Venmo",
  ...
}
```

### Field Values

| Field | Possible Values | Description |
|-------|----------------|-------------|
| `Fleet Dues 2025` | `Paid` or `Unpaid` | Current payment status |
| `Fleet Dues Payment Date` | `YYYY-MM-DD` or empty | Date payment received |
| `Fleet Dues Payment Method` | `Venmo`, `Check`, `Online`, `Cash`, or empty | How they paid |

## How to Update Fleet Dues

### Method 1: Direct JSON Edit (Recommended)
1. Open `data/boats/boats_fleet22.json` in your editor
2. Find the boat by Hull Number
3. Update the payment fields:
   ```json
   "Fleet Dues 2025": "Paid",
   "Fleet Dues Payment Date": "2025-10-07",
   "Fleet Dues Payment Method": "Venmo"
   ```
4. Save the file (automatic backup is created)

### Method 2: Using manage_boat_data.py Tool
```bash
# Update a single boat's Fleet Dues payment
python scripts/processors/manage_boat_data.py update \
  --hull 144 \
  --type fleet \
  --paid \
  --date "2025-10-07" \
  --method "Venmo"

# Mark as unpaid
python scripts/processors/manage_boat_data.py update \
  --hull 144 \
  --type fleet
```

## Workflow

### When Payment Received:
1. **Update boats_fleet22.json**:
   - Set `Fleet Dues 2025` to `"Paid"`
   - Set `Fleet Dues Payment Date` to actual date (YYYY-MM-DD)
   - Set `Fleet Dues Payment Method` to payment method used
   - Optionally add note in `Notes` field

2. **Commit changes** (optional):
   ```bash
   git add data/boats/boats_fleet22.json
   git commit -m "Update Fleet Dues: Hull 144 paid via Venmo"
   git push
   ```

3. **Verify on website**:
   - Your HTML pages will automatically display the updated status

### Generate Reports:
```bash
# View current payment statistics
python scripts/processors/manage_boat_data.py report

# Sync Class Dues and generate full report
python scripts/processors/update_payment_status.py
```

## Class Dues Synchronization

Class Dues are **automatically synced** from J/105 membership data:
- Source: `data/members/j105_members_status.json`
- Run: `python scripts/processors/update_payment_status.py`
- Frequency: Weekly (via GitHub Actions)

**Important**: Don't manually edit Class Dues fields - they will be overwritten by the sync script.

## Quick Reference

### Check Payment Status
```bash
python scripts/processors/manage_boat_data.py report
```

Output:
```
PAYMENT STATUS REPORT - 2025
============================
Total Boats: 20

Fleet Dues 2025:
  Paid: 5 (25.0%)
  Unpaid: 15 (75.0%)

Class Dues 2025:
  Paid: 10 (50.0%)
  Unpaid: 10 (50.0%)
```

### Mark Multiple Boats as Paid
Edit `boats_fleet22.json` in batch - find all boats that paid and update their fields in one edit session.

### Generate Follow-up Report for Unpaid Boats
```bash
python scripts/reports/generate_payment_followup.py
```

This creates a report of unpaid boats with contact info for follow-up.

## Tips

✅ **Use consistent date format**: YYYY-MM-DD (e.g., 2025-10-07)  
✅ **Keep payment methods standardized**: Venmo, Check, Online, Cash  
✅ **Add notes for special cases**: Use the `Notes` field  
✅ **Commit after updates**: Track payment history in git  
✅ **Backup preserved**: Every save creates automatic backup  

❌ **Don't edit Class Dues manually**: They're auto-synced from membership data  
❌ **Don't delete payment fields**: Keep structure consistent  

## GitHub Actions Integration

The weekly GitHub Actions workflow:
1. Scrapes latest boat and membership data
2. **Preserves your manual Fleet Dues edits** ✅
3. Auto-syncs Class Dues from membership data
4. Generates payment reports
5. Commits changes if any updates

Your manual Fleet Dues updates are **always preserved** during automated runs.

## Support

- **Payment tracker**: `python scripts/reports/payment_tracker.py`
- **Follow-up reports**: `python scripts/reports/generate_payment_followup.py`
- **Boat data manager**: `python scripts/processors/manage_boat_data.py`
- **Payment sync**: `python scripts/processors/update_payment_status.py`
