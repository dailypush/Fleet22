# Payment collection

Use the [fleet dues manual](FLEET_DUES_MANUAL.md) for current commands and data format.

1. Create the current-season tracker with `python -m scripts.reports.payment_tracker create`.
2. Record received payments using the tracker command or its `Paid YYYY` column. Keep dates, methods and amounts in the CSV.
3. Apply confirmed payments with `python -m scripts.processors.manage_boat_data merge`.
4. Review with `python -m scripts.processors.manage_boat_data report`.
5. Generate fleet-payment follow-up lists with `python -m scripts.reports.generate_payment_followup`.
6. Review and commit the boat JSON to publish the updated website.

Fleet follow-up reports use manual Fleet Dues, independently of class membership. The current estimate uses $150 per boat. The default tracker CSV is ignored by Git and must be backed up separately. Existing trackers are never overwritten by creation. NO or blank rows do not clear a payment during import; use an explicit `--not-paid` manual correction when needed.

The public status page is [Fleet Dues](https://fleet22.us/pages/fleetdues.html).
