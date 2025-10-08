# Payment Data Preservation in boats_fleet22.json

## Issue Identified
The `boats_fleet22.json` file was losing payment status fields (`Fleet Dues 2025`, `Class Dues 2025`, payment dates, methods, etc.) when scrapers updated the boat list from the HTML table.

## Root Cause
The HTML table in `pages/members.html` only contains 3 columns:
- Hull Number
- Boat Name  
- Yacht Club

When scrapers (`scrape_fleet_boats.py` and `scrape_fleet_boats_local.py`) extracted data from this table, they were overwriting the entire JSON file with only these 3 fields, **losing all payment tracking data**.

## Solution Implemented

### 1. Enhanced Data Structure
Added payment tracking fields to `boats_fleet22.json`:
```json
{
    "Hull Number": "144",
    "Boat Name": "Fall Line",
    "Yacht Club": "EYC",
    "Owner": "",
    "Contact Email": "",
    "Fleet Dues 2025": "Paid",
    "Fleet Dues Payment Date": "2025-09-15",
    "Fleet Dues Payment Method": "Venmo",
    "Class Dues 2025": "Unknown",
    "Class Dues Payment Date": "",
    "Notes": ""
}
```

### 2. Updated Scrapers to Preserve Payment Data

#### `scrape_fleet_boats_local.py`
- Added `load_existing_payment_data()` function to extract payment info before scraping
- Added `merge_payment_data()` function to combine scraped boat list with existing payment data
- **Key behavior:** Preserves payment fields for existing boats, initializes fields for new boats

#### `scrape_fleet_boats.py`
- Added `extract_payment_data()` function to save payment info from existing data
- Added `merge_payment_data()` function to restore payment info after scraping
- Updated main logic to:
  1. Load existing data and extract payment info
  2. Get fresh boat list from HTML
  3. Merge fresh list with preserved payment data
  4. Save combined data

### 3. New Data Management Tool

Created `scripts/processors/manage_boat_data.py` with commands:

#### `enhance` - Add payment fields to all boats
```bash
python scripts/processors/manage_boat_data.py enhance
```

#### `update` - Update payment status for a specific boat
```bash
python scripts/processors/manage_boat_data.py update \
  --hull 144 \
  --type fleet \
  --paid \
  --date 2025-09-15 \
  --method Venmo
```

#### `merge` - Import payment data from payment_tracker CSV
```bash
python scripts/processors/manage_boat_data.py merge
```

#### `report` - View current payment status
```bash
python scripts/processors/manage_boat_data.py report
```

## Payment Data Fields

### Fleet Dues Tracking
- `Fleet Dues 2025`: "Paid" | "Unpaid"
- `Fleet Dues Payment Date`: "YYYY-MM-DD"
- `Fleet Dues Payment Method`: "Venmo" | "Check" | "Online" | "Cash"

### Class Dues Tracking
- `Class Dues 2025`: "Paid" | "Unpaid" | "Unknown"
- `Class Dues Payment Date`: "YYYY-MM-DD"

### Contact & Notes
- `Owner`: Boat owner name
- `Contact Email`: Owner email address
- `Notes`: Any additional notes

## Workflow Integration

### When Scraping Boat Data
The scrapers now automatically:
1. ✅ Load existing payment data BEFORE scraping
2. ✅ Extract boat list from HTML
3. ✅ Merge boat list WITH existing payment data
4. ✅ Save combined data (with automatic backup)

### When Recording Payments
Two methods available:

#### Method 1: Payment Tracker (Recommended)
```bash
# Record in tracker
python scripts/reports/payment_tracker.py update --hull 144 --paid --method Venmo

# Merge tracker data into boats_fleet22.json
python scripts/processors/manage_boat_data.py merge
```

#### Method 2: Direct Update
```bash
python scripts/processors/manage_boat_data.py update \
  --hull 144 \
  --type fleet \
  --paid \
  --date 2025-09-15 \
  --method Venmo
```

## Web Page Integration

The `boats_fleet22.json` file can now be consumed by web pages to display payment status:

```javascript
// Example: Load and display boat data with payment status
fetch('data/boats/boats_fleet22.json')
  .then(response => response.json())
  .then(boats => {
    boats.forEach(boat => {
      console.log(`${boat['Boat Name']}: ${boat['Fleet Dues 2025']}`);
      // Display paid/unpaid status badge
      // Show payment date if available
    });
  });
```

### Suggested HTML Table Enhancement
Add payment status columns to `pages/members.html`:

```html
<table class="table table-striped">
  <thead>
    <tr>
      <th>Hull Number</th>
      <th>Boat Name</th>
      <th>Yacht Club</th>
      <th>Fleet Dues</th>  <!-- NEW -->
      <th>Class Dues</th>  <!-- NEW -->
    </tr>
  </thead>
  <tbody id="boats-table">
    <!-- Populated dynamically from boats_fleet22.json -->
  </tbody>
</table>
```

## Testing

### Verify Payment Data Preservation
```bash
# 1. Check current payment status
python scripts/processors/manage_boat_data.py report

# 2. Run scraper (should preserve payment data)
python scripts/scrapers/scrape_fleet_boats_local.py

# 3. Verify payment data still intact
python scripts/processors/manage_boat_data.py report
```

### Expected Result
```
Total Boats:           20
Fleet Dues 2025:
  Paid:                5 (25.0%)
  Unpaid:              15 (75.0%)
```

Payment data should remain unchanged after scraping!

## Current Status

✅ **Problem Solved!**
- Payment fields added to all 20 boats
- 5 boats marked as paid (from payment tracker)
- Scrapers updated to preserve payment data
- Management tools created for easy updates
- Automatic backups protect against data loss

## Files Modified

### Scrapers (Updated)
- `scripts/scrapers/scrape_fleet_boats.py`
- `scripts/scrapers/scrape_fleet_boats_local.py`

### New Tools
- `scripts/processors/manage_boat_data.py`

### Data Files
- `data/boats/boats_fleet22.json` - Now includes payment fields
- `data/payments/payment_tracker_2025.csv` - CSV-based tracking

## Recommendations

1. **Keep both tracking systems in sync:**
   - Update payment_tracker.csv when receiving payments
   - Regularly merge tracker data into boats_fleet22.json
   - Use `manage_boat_data.py merge` command weekly

2. **Update the HTML table:**
   - Add payment status columns to members.html
   - Load data dynamically from boats_fleet22.json
   - Display payment badges (Paid/Unpaid)

3. **Automate synchronization:**
   - Add merge step to GitHub Actions workflow
   - Run after scraping boat data
   - Ensures payment data always preserved

4. **Regular backups:**
   - Automatic backups created on every save
   - Located in `data/boats/boats_fleet22_backup_*.json`
   - Keep last 10 backups for safety

---

*Last Updated: October 7, 2025*
*Issue Resolution: Complete ✅*
