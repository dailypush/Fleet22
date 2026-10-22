#!/usr/bin/env python3
"""Validate every record in all three fleet source snapshots."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_json
from utils.logger import setup_logger
from utils.path_utils import BOATS_FILE, MEMBERS_FILE, SAILS_FILE
from utils.validation import validate_records

logger = setup_logger('validator')


def validate_file(filepath, kind):
    try:
        validate_records(load_json(filepath), kind)
        return True
    except (OSError, ValueError, TypeError) as error:
        logger.error("%s: %s", filepath, error)
        return False


def validate_sail_tags_data(filepath):
    return validate_file(filepath, 'sails')


def validate_membership_data(filepath):
    return validate_file(filepath, 'members')


def validate_fleet_boats_data(filepath):
    return validate_file(filepath, 'boats')


def run_validations():
    results = [validate_file(path, kind) for path, kind in (
        (SAILS_FILE, 'sails'), (MEMBERS_FILE, 'members'), (BOATS_FILE, 'boats'))]
    return all(results)


if __name__ == '__main__':
    sys.exit(0 if run_validations() else 1)
