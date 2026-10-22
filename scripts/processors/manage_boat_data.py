#!/usr/bin/env python3
"""Explicit manual Fleet Dues updates using the simplified boat schema.

Payment dates, methods and amounts belong in the season's CSV tracker.
Class Dues are synchronized from membership by update_payment_status.py.
"""
import argparse
import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_json, save_json
from utils.path_utils import BOATS_FILE, PAYMENTS_DATA
from utils.validation import validate_records

CURRENT_YEAR = date.today().year
BOAT_SCHEMA = {
    'Hull Number': '', 'Boat Name': '', 'Yacht Club': '',
    'Fleet Dues': 'Not Paid', 'Class Dues': 'Not Paid',
}


def load_boats_data():
    data = load_json(BOATS_FILE)
    validate_records(data, 'boats')
    return data


def enhance_boat_data(boats_data):
    """Fill current fields without adding legacy payment columns."""
    count = 0
    for boat in boats_data:
        for field, default in BOAT_SCHEMA.items():
            if field not in boat:
                boat[field] = default
                count += 1
    validate_records(boats_data, 'boats')
    return boats_data, count


def update_boat_payment(boats_data, hull_number, dues_type='fleet', paid=True):
    if dues_type != 'fleet':
        raise ValueError('Class Dues must be synced from class membership')
    validate_records(boats_data, 'boats')
    for boat in boats_data:
        if boat['Hull Number'] == str(hull_number):
            boat['Fleet Dues'] = 'Paid' if paid else 'Not Paid'
            return True
    return False


def merge_with_tracker(boats_data, tracker_csv_path):
    """Apply confirmed payments only; blank/NO rows never clear manual dues."""
    validate_records(boats_data, 'boats')
    paid_column = f'Paid {CURRENT_YEAR}'
    with Path(tracker_csv_path).open(newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        if not {'Hull', paid_column}.issubset(reader.fieldnames or []):
            raise ValueError(f'Tracker must contain Hull and {paid_column}')
        payments = set()
        seen = set()
        for row in reader:
            hull = row['Hull'].strip()
            status = row[paid_column].strip().upper()
            if hull in seen or not hull.isdigit() or status not in {'YES', 'NO', ''}:
                raise ValueError(f'Invalid or duplicate tracker row for hull {hull}')
            seen.add(hull)
            if status == 'YES':
                payments.add(hull)
    unknown = payments - {b['Hull Number'] for b in boats_data}
    if unknown:
        raise ValueError(f'Paid hulls missing from fleet roster: {sorted(unknown)}')
    updated = 0
    for boat in boats_data:
        if boat['Hull Number'] in payments and boat['Fleet Dues'] != 'Paid':
            boat['Fleet Dues'] = 'Paid'
            updated += 1
    return boats_data, updated


def generate_report(boats_data):
    total = len(boats_data)
    print(f'Fleet 22 dues — {CURRENT_YEAR}: {total} boats')
    for field in ('Fleet Dues', 'Class Dues'):
        paid = sum(b[field] == 'Paid' for b in boats_data)
        print(f'{field}: {paid} paid, {total - paid} not paid')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['enhance', 'update', 'merge', 'report'])
    parser.add_argument('--hull')
    parser.add_argument('--type', choices=['fleet'], default='fleet')
    status = parser.add_mutually_exclusive_group()
    status.add_argument('--paid', action='store_true')
    status.add_argument('--not-paid', action='store_true')
    parser.add_argument('--tracker', type=Path,
                        default=PAYMENTS_DATA / f'payment_tracker_{CURRENT_YEAR}.csv')
    args = parser.parse_args()
    try:
        boats = load_boats_data()
        if args.action == 'update':
            if not args.hull or not (args.paid or args.not_paid):
                parser.error('update requires --hull and either --paid or --not-paid')
            if not update_boat_payment(boats, args.hull, paid=args.paid):
                raise ValueError(f'Hull {args.hull} not found')
        elif args.action == 'merge':
            boats, _ = merge_with_tracker(boats, args.tracker)
        elif args.action == 'enhance':
            boats, _ = enhance_boat_data(boats)
        if args.action != 'report':
            validate_records(boats, 'boats')
            save_json(boats, BOATS_FILE)
        generate_report(boats)
        return 0
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
