# Fleet Dues Data Format

## Overview
Fleet dues data uses a simplified format that is easy to update and reset each sailing season.

## Data Structure

### Simplified Format (Current)
The fleet dues data in `data/boats/boats_fleet22.json` uses a simple, season-agnostic format:

```json
{
    "Hull Number": "493",
    "Boat Name": "Rapscallion",
    "Yacht Club": "EYC",
    "Fleet Dues": "Paid",
    "Class Dues": "Not Paid"
}
```

### Field Descriptions

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `Hull Number` | String | Any valid J/105 hull number | Unique identifier for the boat |
| `Boat Name` | String | Any string | Name of the boat |
| `Yacht Club` | String | Any string | Home yacht club abbreviation |
| `Fleet Dues` | String | `"Paid"` or `"Not Paid"` | Fleet 22 dues payment status for current season |
| `Class Dues` | String | `"Paid"` or `"Not Paid"` | J/105 Class Association dues status for current season |

## Benefits of Simplified Format

1. **Easy to Reset**: At the start of each season, simply set all `Fleet Dues` and `Class Dues` to `"Not Paid"`
2. **Simple to Update**: Change status from `"Not Paid"` to `"Paid"` as payments arrive
3. **No Year Management**: No need to track year-specific fields or payment dates
4. **Clean Display**: Works perfectly with the fleet dues status page
5. **Less Maintenance**: Fewer fields mean less data to manage

## Season Reset Process

At the beginning of each sailing season:

1. Run the reset script:
   ```bash
   python3 scripts/utils/reset_dues_season.py
   ```
   
   Or manually update all entries to:
   ```json
   "Fleet Dues": "Not Paid",
   "Class Dues": "Not Paid"
   ```

2. As payments arrive, update individual boats:
   ```json
   "Fleet Dues": "Paid",
   "Class Dues": "Paid"
   ```

## Updating Payment Status

### Manual Updates
Edit `data/boats/boats_fleet22.json` directly:
```json
{
    "Hull Number": "246",
    "Boat Name": "Mr. Krabs",
    "Yacht Club": "BHSC",
    "Fleet Dues": "Paid",        // ← Change from "Not Paid" to "Paid"
    "Class Dues": "Paid"
}
```

### Automated Class Dues Sync
Class dues can be automatically synced from J/105 membership data:
```bash
python3 scripts/processors/update_payment_status.py
```

This will:
- Update Class Dues based on current J/105 membership records
- Preserve Fleet Dues status (manually maintained)
- Generate summary reports

## Web Page Integration

The simplified format works seamlessly with `pages/fleetdues.html`:

```javascript
```javascript
fetch('https://api.github.com/repos/dailypush/Fleet22/contents/data/boats/boats_fleet22.json')
    .then(response => response.json())
    .then(data => {
        const content = atob(data.content);
        const boatsData = JSON.parse(content);
        // Use boatsData...
    });
```
```

## Migration from Detailed Format

If you have the old detailed format with year-specific fields:
```json
{
    "Fleet Dues 2025": "Paid",
    "Fleet Dues Payment Date": "2025-09-22",
    "Fleet Dues Payment Method": "Check"
}
```

Convert to simplified format using:
```bash
python3 scripts/utils/simplify_dues_format.py
```

## File Locations

- **Single Source of Truth**: `data/boats/boats_fleet22.json` (auto-updated by GitHub Actions)
- **Conversion Script**: `scripts/utils/simplify_dues_format.py`
- **Reset Script**: `scripts/utils/reset_dues_season.py`

## Notes

- Fleet Dues are always manually maintained
- Class Dues can be synced from J/105 membership data
- The file is automatically updated by GitHub Actions workflow
- The web page loads from the GitHub API, so commit changes to make them visible online
