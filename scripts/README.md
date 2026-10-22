# Fleet 22 scripts

Run commands from the repository root with Python 3.10 or newer.

```bash
pip install -r scripts/requirements-scraping.lock
python -m unittest discover -s tests -v
python -m scripts.update_all_data
```

The update stages membership → sail tags → fleet roster → validation → combined data, then publishes validated files and freshness metadata. It preserves manual Fleet Dues. Individual modules can still be run for troubleshooting, but the staged updater provides whole-pipeline validation before publication.

```bash
python -m scripts.validators.validate_fleet_data
python -m scripts.processors.manage_boat_data report
python -m scripts.processors.manage_boat_data update --hull 493 --paid
python -m scripts.reports.payment_tracker create
python -m scripts.processors.manage_boat_data merge
python -m scripts.reports.generate_payment_followup
python -m scripts.generate_site --check
python -m scripts.validators.check_site
```

Install `scripts/requirements.txt` for optional pandas/matplotlib/seaborn analysis. CI only installs the scraping lockfile. To update that lock, install `scripts/requirements-scraping.txt` in a clean Python 3.10+ environment, run the tests, and regenerate with `pip freeze`.

Shared code:

- `utils/membership.py`: season rules, co-owner grouping and representative ownership.
- `utils/validation.py`: source schemas and snapshot comparison.
- `utils/data_loader.py`: UTF-8 JSON, original-file backups and atomic writes.
- `utils/http_client.py`: verified HTTPS, timeouts and bounded GET retries.
- `utils/path_utils.py`: paths; `FLEET22_DATA_DIR` selects an isolated staging data directory.
- `utils/logger.py`: file and console logging.

See the root [README](../README.md) and [dues manual](../FLEET_DUES_MANUAL.md) for the data contract and payment workflow.
