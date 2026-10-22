# Fleet dues manual

Fleet Dues are manually maintained in `data/boats/boats_fleet22.json`. Class Dues are calculated from class membership. Boat JSON uses the year-independent keys `Fleet Dues` and `Class Dues`, with values `Paid` or `Not Paid`; hull numbers are strings.

Run from the repository root using the project's Python environment:

```bash
python -m scripts.processors.manage_boat_data update --hull 493 --paid
python -m scripts.processors.manage_boat_data update --hull 493 --not-paid
python -m scripts.processors.manage_boat_data report
```

The update command requires an explicit payment status. It changes Fleet Dues only and backs up the original JSON before writing. Class Dues are synchronized with:

```bash
python -m scripts.processors.update_payment_status
```

Any co-owner's full `Member YYYY` status for the current calendar year counts as paid Class Dues. Associate membership alone does not. Fleet Dues stay unchanged. This command intentionally regenerates payment reports; the regular registry updater does not overwrite manually edited reports.

## Payment tracker

```bash
python -m scripts.reports.payment_tracker create
python -m scripts.reports.payment_tracker update --hull 493 --paid --method Venmo
python -m scripts.reports.payment_tracker summary
python -m scripts.processors.manage_boat_data merge
```

The default path is `data/payments/payment_tracker_YYYY.csv`, with a matching `Paid YYYY` column. Dates, methods and amounts stay in this CSV, not boat JSON. Creation refuses to overwrite an existing CSV and initializes status from the current manual Fleet Dues. Import applies YES rows only, preserving existing payments for NO or blank rows; duplicate hulls, unknown paid hulls and old-season headers cause errors.

## New season

A season reset is an explicit administrative action, never part of scraping:

```bash
python -m scripts.utils.reset_dues_season --fleet-only
```

This preserves class status, prompts before resetting manual Fleet Dues, and backs up the original bytes. Without `--fleet-only`, the existing reset command also clears Class Dues; the next membership sync recalculates them. Restore a backup by copying it over the source JSON if necessary.

## Legacy migration

For older year-specific boat JSON, first copy it to a separate file and run:

```bash
python -m scripts.utils.simplify_dues_format legacy-boats.json converted-boats.json
```

Existing simplified dues take precedence; otherwise the converter uses the latest legacy year per dues type. Review the result and season before adopting it. The converter creates a backup before replacing any existing output.

Never assume a previous year's payment covers the new season. Keep payment records and manually reconcile any boat that leaves the registry while it has paid dues.
