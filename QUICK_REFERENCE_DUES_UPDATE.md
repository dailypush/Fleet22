# Dues quick reference

Run from the repository root with the project Python environment:

```bash
# Record a manual Fleet Dues payment.
python -m scripts.processors.manage_boat_data update --hull 493 --paid
# Correct a manual status.
python -m scripts.processors.manage_boat_data update --hull 493 --not-paid
# Review status.
python -m scripts.processors.manage_boat_data report
# Refresh registry data while preserving Fleet Dues.
python -m scripts.update_all_data
# Explicitly regenerate class-payment status and payment reports.
python -m scripts.processors.update_payment_status
```

Use `Fleet Dues` / `Class Dues` with `Paid` / `Not Paid`. Payment details belong in the current-season CSV. See [the complete manual](FLEET_DUES_MANUAL.md).
