# Quick Reference: Updating Fleet Dues

## Manual Update Process

When you receive a payment, simply edit `data/boats/boats_fleet22.json`:

### Example 1: Mark Fleet Dues as Paid

**Find the boat entry:**
```json
{
    "Hull Number": "493",
    "Boat Name": "Rapscallion",
    "Yacht Club": "EYC",
    "Fleet Dues": "Not Paid",
    "Class Dues": "Not Paid"
}
```

**Change Fleet Dues to Paid:**
```json
{
    "Hull Number": "493",
    "Boat Name": "Rapscallion",
    "Yacht Club": "EYC",
    "Fleet Dues": "Paid",        ← Changed
    "Class Dues": "Not Paid"
}
```

### Example 2: Mark Both Dues as Paid

```json
{
    "Hull Number": "493",
    "Boat Name": "Rapscallion",
    "Yacht Club": "EYC",
    "Fleet Dues": "Paid",        ← Changed
    "Class Dues": "Paid"         ← Changed
}
```

## After Updating

1. **Save the file**
2. **Commit and push**:
   ```bash
   git add data/boats/boats_fleet22.json
   git commit -m "Update dues status for Hull 493"
   git push
   ```
3. **Verify** on the website: https://fleet22.us/pages/fleetdues.html

## Valid Values

- `"Paid"` - Dues have been paid
- `"Not Paid"` - Dues have not been paid

**Note:** Use exactly these values with proper capitalization and quotes.

## Quick Find & Replace (Multiple Boats)

If you need to update multiple boats at once, you can use your editor's find/replace:

**Find:** `"Fleet Dues": "Not Paid",`
**Replace with:** `"Fleet Dues": "Paid",`

Then manually revert any boats that shouldn't be changed.

## Season Reset (New Year)

At the start of a new season, reset all dues:

```bash
cd /Users/chad/Projects/Fleet22_us
python3 scripts/utils/reset_dues_season.py
```

This will:
- Set all Fleet Dues to "Not Paid"
- Set all Class Dues to "Not Paid"
- Create a backup before changes
- Update both file locations

## Troubleshooting

### Website not updating?
- Check that you committed and pushed changes
- Wait 1-2 minutes for GitHub Pages to rebuild
- Clear browser cache (Cmd+Shift+R on Mac)

### JSON format error?
- Make sure you didn't introduce a syntax error
- Check for missing commas or quotes
- Validate JSON at https://jsonlint.com

### Can't find a boat?
- Search for the hull number: Cmd+F then type hull number
- Boats are not in any particular order in the file
