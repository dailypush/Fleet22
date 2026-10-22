# Payment data preservation

The current boat schema uses `Fleet Dues` and `Class Dues`, each `Paid` or `Not Paid`. See [the dues manual](FLEET_DUES_MANUAL.md).

- Scraping preserves manual Fleet Dues and yacht club by hull number. Corrupt or missing baseline boat data stops the builder rather than resetting payments.
- Class Dues use the same current-season full-membership rule in both the fleet builder and payment synchronizer, including all co-owner records.
- Empty extraction, malformed rows, suspicious dataset shrinkage and removal of paid boats stop publication.
- The updater stages the complete refresh and checks that source files have not changed locally before publishing. Scrape/processing failures leave published snapshots unchanged.
- JSON writes back up original bytes and atomically replace individual files. An interrupted serialization or replacement preserves the destination. Files are validated together before publication; a disk error during publication can still interrupt the sequence of individual file replacements.
- CSV imports accept only the current season's header and apply confirmed YES payments. NO/blank entries preserve manual payments.
- Season reset and format conversion use the shared backup/atomic-write helper. Conversion preserves already-simplified payments.
- Payment sync reports are regenerated only by the explicit payment synchronization command; routine registry refreshes leave them alone.

Run `python -m unittest discover -s tests -v` to verify these contracts offline. Backups are ignored by Git; preserve an independent copy of manually maintained payment trackers.
