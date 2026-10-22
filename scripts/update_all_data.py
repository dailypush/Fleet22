#!/usr/bin/env python3
"""Stage, validate and publish a complete refresh; preserve manual payments."""
import hashlib
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .utils.data_loader import load_json, save_json
from .utils.path_utils import DATA_DIR, PROJECT_ROOT

SOURCE_FILES = ('members/j105_members_status.json', 'sails/sail_tags.json', 'boats/boats_fleet22.json')
PUBLISHED_FILES = (*SOURCE_FILES, 'combined/combined_fleet_data.json', 'combined/fleet_statistics.json')


def main():
    # All subprocesses work on isolated copies until the whole pipeline passes.
    with tempfile.TemporaryDirectory(prefix='fleet22-refresh-') as temporary:
        staged = Path(temporary)
        originals = {}
        for relative in SOURCE_FILES:
            destination = staged / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            original = (DATA_DIR / relative).read_bytes()
            destination.write_bytes(original)
            originals[relative] = original
        environment = {**os.environ, 'FLEET22_DATA_DIR': str(staged)}
        for module in ('scrapers.scrape_owner_status', 'scrapers.scrape_sail_tags',
                       'scrapers.scrape_fleet_boats', 'validators.validate_fleet_data',
                       'processors.combine_data_sources'):
            subprocess.run([sys.executable, '-m', f'scripts.{module}'], cwd=PROJECT_ROOT,
                           env=environment, check=True)
        for relative, original in originals.items():
            if (DATA_DIR / relative).read_bytes() != original:
                raise RuntimeError(f'{relative} changed during refresh; keeping the local edit')
        metadata = {'checked_at': datetime.now(timezone.utc).isoformat(), 'files': {}}
        for relative in PUBLISHED_FILES:
            data = load_json(staged / relative)
            if not (DATA_DIR / relative).exists() or load_json(DATA_DIR / relative) != data:
                save_json(data, DATA_DIR / relative)
            metadata['files'][relative] = {
                'records': len(data),
                'sha256': hashlib.sha256((DATA_DIR / relative).read_bytes()).hexdigest(),
            }
        # Publish freshness last, only after the full validated refresh succeeds.
        save_json(metadata, DATA_DIR / 'metadata.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
