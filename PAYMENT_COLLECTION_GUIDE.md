# Fleet 22 Payment Collection & Tracking Guide

## Overview
This guide explains how to track and collect fleet dues payments for Fleet 22 boats using the automated payment tracking system.

**Annual Fleet Dues:** $150 per boat  
**Payment Methods:** Venmo, Check, Online, Cash  

---

## Quick Start

### 1. View Current Payment Status
```bash
python scripts/reports/payment_tracker.py summary
```

### 2. Generate Follow-up Report
```bash
python scripts/reports/generate_payment_followup.py
```
This creates a detailed report at: `data/payments/payment_followup_report.txt`

### 3. Record a Payment
```bash
python scripts/reports/payment_tracker.py update \
  --hull 144 \
  --paid \
  --method Venmo \
  --date 2025-09-15
```

---

## Files Created

### Payment Tracker CSV
**Location:** `data/payments/payment_tracker_2025.csv`

This CSV file tracks all payment details and can be edited directly or via command line.

**Columns:**
- `Hull` - Boat hull number
- `Boat Name` - Name of the boat
- `Yacht Club` - Home yacht club
- `Paid 2025` - YES/NO payment status
- `Payment Date` - Date payment received (YYYY-MM-DD)
- `Payment Method` - Venmo, Check, Online, Cash, Other
- `Amount` - Payment amount (usually $150)
- `Contact Email` - Owner contact information
- `Notes` - Any additional notes

### Follow-up Report
**Location:** `data/payments/payment_followup_report.txt`

Comprehensive report including:
- Executive summary with statistics
- Unpaid boats grouped by yacht club
- Complete unpaid boats list
- Recommended action items
- Email template for follow-up

---

## Usage Examples

### Create Fresh Payment Tracker
```bash
# Creates new CSV with all boats marked unpaid
python scripts/reports/payment_tracker.py create
```

### Record Multiple Payments
```bash
# Mark several boats as paid
python scripts/reports/payment_tracker.py update --hull 144 --paid --method Venmo --date 2025-09-15
python scripts/reports/payment_tracker.py update --hull 145 --paid --method Online --date 2025-09-20
python scripts/reports/payment_tracker.py update --hull 246 --paid --method Check --date 2025-09-22
```

### View Summary Statistics
```bash
python scripts/reports/payment_tracker.py summary
```

**Output Example:**
```
FLEET 22 PAYMENT TRACKER SUMMARY
================================================================================
Total Boats:       20
Paid:              5 (25.0%)
Unpaid:            15 (75.0%)
Total Collected:   $750.00
Outstanding:       $2,250.00 (est.)

UNPAID BOATS:
--------------------------------------------------------------------------------
  Hull   10 | Zamboni                        |           
  Hull   37 | Windependence                  | BHSC      
  ...
```

### Generate Club-Specific Report
```bash
# Generate report for specific yacht club
python scripts/reports/generate_payment_followup.py --club EYC
```

---

## Payment Collection Workflow

### Step 1: Generate Initial Report (Beginning of Season)
```bash
# Create payment tracker for new season
python scripts/reports/payment_tracker.py create

# Generate follow-up report
python scripts/reports/generate_payment_followup.py

# Review unpaid boats by yacht club
cat data/payments/payment_followup_report.txt
```

### Step 2: Send Reminders
Use the email template from the follow-up report to contact yacht club fleet captains:

**Email Subject:** Fleet 22 Dues Payment Reminder - [Yacht Club Name]

**Key Points to Include:**
- List of unpaid boats from their club
- Payment amount: $150/boat
- Payment methods: Venmo (@fleet22lakerie), Check, Online
- Benefits: Website, regatta support, class resources
- Deadline: Set reasonable deadline (e.g., 30 days)

### Step 3: Record Payments as Received
```bash
# When payment received via Venmo
python scripts/reports/payment_tracker.py update \
  --hull 423 \
  --paid \
  --method Venmo \
  --date 2025-10-07

# When check received
python scripts/reports/payment_tracker.py update \
  --hull 638 \
  --paid \
  --method Check \
  --date 2025-10-08

# Check updated status
python scripts/reports/payment_tracker.py summary
```

### Step 4: Follow-up on Unpaid Boats (After Deadline)
```bash
# Generate updated report showing remaining unpaid
python scripts/reports/generate_payment_followup.py

# Send second reminder to yacht clubs with unpaid boats
# Consider adding late fee notice if applicable
```

### Step 5: Final Collection Efforts
- Direct email to boat owners (if contact info available)
- Reach out to yacht club secretaries
- Consider late fee policy
- Update tracker with any special arrangements

---

## Manual CSV Editing

You can also edit the CSV file directly in Excel, Numbers, or any spreadsheet application:

1. Open `data/payments/payment_tracker_2025.csv`
2. Update `Paid 2025` column to "YES"
3. Fill in `Payment Date`, `Payment Method`, `Amount`
4. Add `Contact Email` and `Notes` as needed
5. Save the file

Then run summary to see updated statistics:
```bash
python scripts/reports/payment_tracker.py summary
```

---

## Yacht Club Breakdown (Current Fleet)

Based on `boats_fleet22.json`:

| Yacht Club | Boats | Notes |
|------------|-------|-------|
| EYC        | 7     | Largest fleet contingent |
| BHSC       | 4     | Bay Haven Sailing Club |
| NCYC       | 3     | North Coast Yacht Club |
| BYC        | 2     | Buffalo Yacht Club |
| SSC        | 1     | Sandusky Sailing Club |
| GRSC       | 1     | Grand River Sailing Club |
| Unknown    | 2     | No club affiliation listed |

**Follow-up Priority:** Focus on EYC and BHSC first (largest groups)

---

## Payment Method Information

### Venmo
- Handle: `@fleet22lakerie`
- Fastest payment method
- No fees
- Immediate notification

### Check
- Payable to: Fleet 22 Lake Erie
- Mail to: [Treasurer Address]
- Include hull number in memo

### Online
- Website: https://fleet22.us/fleetdues.html
- PayPal or credit card options
- Small processing fee may apply

### Cash
- In-person at regattas
- Provide receipt
- Update tracker immediately

---

## Reporting & Analytics

### Current Season Statistics
```bash
# Quick summary
python scripts/reports/payment_tracker.py summary

# Detailed follow-up report
python scripts/reports/generate_payment_followup.py

# Club-specific analysis
python scripts/reports/generate_payment_followup.py --club EYC
python scripts/reports/generate_payment_followup.py --club BHSC
```

### Export for Treasurer
The CSV file `payment_tracker_2025.csv` can be:
- Shared with treasurer via email
- Imported into accounting software
- Used for annual financial reports
- Archived for historical records

---

## Tips for Successful Collection

### Best Practices
1. **Send early reminders** - Start communication in spring before racing season
2. **Use yacht club contacts** - Fleet captains can help spread the word
3. **Emphasize benefits** - Remind members what dues support
4. **Make payment easy** - Multiple payment methods increase collection rate
5. **Track promptly** - Update tracker immediately when payments received
6. **Follow up consistently** - Gentle reminders work better than single requests

### Communication Templates
The follow-up report includes a professional email template. Customize it with:
- Your contact information
- Specific yacht club details
- Payment deadline
- Any special notes or events

### Incentives to Consider
- Early bird discount (paid by certain date)
- Recognition of paid boats on website
- Priority registration for special events
- Thank you notes to yacht clubs with 100% payment

---

## Troubleshooting

### Problem: Boat not in tracker
**Solution:** The boat may not be in `boats_fleet22.json`. Add it there first, then recreate tracker.

### Problem: Payment amount different than $150
**Solution:** Use `--amount` flag when updating:
```bash
python scripts/reports/payment_tracker.py update --hull 144 --paid --amount 175
```

### Problem: Need to mark as unpaid (payment reversed)
**Solution:** Update without `--paid` flag:
```bash
python scripts/reports/payment_tracker.py update --hull 144
```

### Problem: Lost tracker file
**Solution:** Recreate from boats data:
```bash
python scripts/reports/payment_tracker.py create
```
Then manually update from payment records.

---

## Files Reference

### Created Scripts
- `scripts/reports/payment_tracker.py` - Main payment tracking tool
- `scripts/reports/generate_payment_followup.py` - Report generator

### Data Files
- `data/payments/payment_tracker_2025.csv` - **Main tracking file**
- `data/payments/payment_followup_report.txt` - Follow-up report
- `data/boats/boats_fleet22.json` - Source boat data

### Logs
- `logs/reports.log` - Activity log for payment operations

---

## Annual Checklist

### Start of Season (March/April)
- [ ] Create fresh payment tracker for new year
- [ ] Generate initial follow-up report
- [ ] Send first reminder to all yacht clubs
- [ ] Post payment information on website

### Mid-Season (May/June)
- [ ] Check payment status weekly
- [ ] Send reminder to unpaid boats
- [ ] Update tracker as payments received
- [ ] Thank yacht clubs with 100% payment

### Late Season (July/August)
- [ ] Final reminder to unpaid boats
- [ ] Consider late fee policy
- [ ] Direct outreach to remaining unpaid
- [ ] Update membership benefits eligibility

### End of Season (September/October)
- [ ] Final collection efforts
- [ ] Generate year-end summary
- [ ] Provide financial report to board
- [ ] Archive payment records

---

## Support

For questions or issues with the payment tracking system:
- Email: info@fleet22.us
- Check logs: `logs/reports.log`
- Review documentation: This guide

---

*Last Updated: October 7, 2025*
*Version: 1.0*
