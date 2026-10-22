"""Offline regressions for payment preservation, parser failures and publication."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

# Existing scripts use utils imports when run as modules or standalone files.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from utils.data_loader import save_json
from utils.membership import best_membership, is_paid_membership, primary_member
from utils.validation import validate_records, validate_update
from scripts.scrapers import scrape_fleet_boats as builder
from scripts.scrapers import scrape_owner_status as owners
from scripts.scrapers import scrape_sail_tags as sails
from scripts.processors import combine_data_sources as combine
from scripts.processors import manage_boat_data as manager
from scripts.processors import update_payment_status as payments
from scripts.reports import payment_tracker as tracker
from scripts.reports.generate_payment_followup import generate_report
from scripts import update_all_data as pipeline
from scripts.utils.reset_dues_season import reset_dues_season
from scripts.utils.simplify_dues_format import convert_to_simplified_format

YEAR = date.today().year
BOAT = {'Hull Number': '1', 'Boat Name': 'Example', 'Yacht Club': 'EYC',
        'Fleet Dues': 'Paid', 'Class Dues': 'Not Paid'}
MEMBER = {'Hull': '1', 'Boat Name': 'Example', 'Owners/Helmsmen': 'Current owner',
          'Fleet': '22', 'Class Membership': f'Member {YEAR}', 'Status': 'OW'}
SAIL = {'Hull': '1', 'Purchaser': 'Historical purchaser', 'Certificate No.': 'ABC123',
        'Sailmaker': 'North', 'Delivery Date': '2020-01-01', 'Sail Type': 'M', 'Fleet': '22', 'Notes': ''}


class DataTests(unittest.TestCase):
    def test_full_validation_rejects_empty_malformed_duplicate_and_bad_dues(self):
        for data in ([], [BOAT, {'bad': 'record'}], [BOAT, BOAT],
                     [dict(BOAT, **{'Fleet Dues': 'Unpaid'})],
                     [dict(BOAT, **{'Fleet Dues 2025': 'Paid'})]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_records(data, 'boats')
        validate_records([BOAT], 'boats')

    def test_suspicious_shrink_and_hull_replacement_fail(self):
        previous = [dict(BOAT, **{'Hull Number': str(i)}) for i in range(10)]
        for data in (previous[:7], [dict(b, **{'Hull Number': str(i + 100)}) for i, b in enumerate(previous)]):
            with self.assertRaises(ValueError):
                validate_update(data, previous, 'boats')

    def test_season_and_associate_rules(self):
        for status, expected in ((f'Member {YEAR}', True), (f'Member {YEAR - 1}', False),
                                 (f'Member {YEAR + 1}', False), (f'Associate {YEAR}', False),
                                 ('Not Member ' + str(YEAR), False), ('', False)):
            with self.subTest(status=status):
                self.assertEqual(is_paid_membership(status, YEAR), expected)

    def test_coowner_order_does_not_change_class_dues(self):
        rows = [dict(MEMBER, **{'Class Membership': f'Associate {YEAR}'}), MEMBER,
                dict(MEMBER, **{'Class Membership': f'Member {YEAR + 1}'})]
        for records in (rows, list(reversed(rows))):
            selected = best_membership(records, YEAR)
            built = builder.merge_preserved_data([{'Hull Number': '1', 'Class Membership': selected}],
                                                  {'1': BOAT})
            synced, _ = payments.sync_class_dues_from_members([copy.deepcopy(BOAT)], records)
            self.assertEqual(built[0]['Class Dues'], 'Paid')
            self.assertEqual(built[0]['Class Dues'], synced[0]['Class Dues'])
            self.assertEqual(built[0]['Fleet Dues'], 'Paid')

    def test_builder_associate_agrees_with_sync(self):
        records = [dict(MEMBER, **{'Class Membership': f'Associate {YEAR}'})]
        built = builder.merge_preserved_data([{'Hull Number': '1', 'Class Membership': records[0]['Class Membership']}], {'1': BOAT})
        synced, _ = payments.sync_class_dues_from_members([copy.deepcopy(BOAT)], records)
        self.assertEqual(built[0]['Class Dues'], 'Not Paid')
        self.assertEqual(built[0]['Class Dues'], synced[0]['Class Dues'])

    def test_builder_refuses_corrupt_existing_payments(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'boats.json'
            path.write_text('{invalid')
            with patch.object(builder, 'BOATS_FILE', path), self.assertRaises(ValueError):
                builder.get_existing_fleet_data()

    def test_builder_refuses_to_remove_paid_boat(self):
        fresh = [{'Hull Number': '2', 'Boat Name': 'New', 'Class Membership': f'Member {YEAR}'}]
        with patch.object(builder, 'get_existing_fleet_data', return_value=[BOAT]), \
             patch.object(builder, 'load_fleet22_from_members', return_value=fresh), \
             patch.object(builder, 'save_json') as save:
            with self.assertRaises(ValueError):
                builder.main()
            save.assert_not_called()

    def test_current_owner_overrides_historical_purchaser(self):
        sources = {combine.SAILS_FILE: [SAIL], combine.MEMBERS_FILE: [MEMBER], combine.BOATS_FILE: [BOAT]}
        with patch.object(combine, 'load_json_data', side_effect=lambda p: copy.deepcopy(sources[p])):
            result = combine.combine_boat_data()
        self.assertEqual(result[0]['owner'], MEMBER['Owners/Helmsmen'])
        with patch.object(combine, 'save_json'):
            stats = combine.generate_fleet_statistics(result)
        self.assertEqual(stats['active_membership'], 1)
        self.assertTrue(stats['generation'].endswith('+00:00'))

    def test_historical_sail_fleet_does_not_count_as_current_membership(self):
        sources = {combine.SAILS_FILE: [SAIL, dict(SAIL, Hull='2')],
                   combine.MEMBERS_FILE: [MEMBER], combine.BOATS_FILE: [BOAT]}
        with patch.object(combine, 'load_json_data', side_effect=lambda p: copy.deepcopy(sources[p])):
            result = combine.combine_boat_data()
        with patch.object(combine, 'save_json'):
            stats = combine.generate_fleet_statistics(result)
        self.assertEqual(stats['fleet_22_boats'], 1)
        self.assertEqual(result[1]['fleet'], '')

    def test_owner_preferred_to_crew_independent_of_order(self):
        crew = dict(MEMBER, Status='CO', **{'Owners/Helmsmen': 'Crew'})
        for rows in ([crew, MEMBER], [MEMBER, crew]):
            self.assertEqual(primary_member(rows)['Owners/Helmsmen'], 'Current owner')

    def test_combiner_refuses_placeholder(self):
        with patch.object(combine, 'ensure_directories'), \
             patch.object(combine, 'combine_boat_data', return_value=[]), \
             patch.object(combine, 'save_json') as save:
            self.assertFalse(combine.main())
            save.assert_not_called()

    def test_atomic_save_keeps_destination_on_serialization_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'boats.json'
            path.write_text(json.dumps([BOAT]))
            original = path.read_bytes()
            with self.assertRaises(TypeError):
                save_json({'invalid': object()}, path)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(len(list(path.parent.glob('*_backup_*.json'))), 1)
            self.assertFalse(list(path.parent.glob('*.tmp')))

    def test_atomic_replace_failure_preserves_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'boats.json'
            save_json([BOAT], path)
            original = path.read_bytes()
            with patch('utils.data_loader.os.replace', side_effect=OSError('interrupted')):
                with self.assertRaises(OSError):
                    save_json([], path)
            self.assertEqual(path.read_bytes(), original)
            self.assertFalse(list(path.parent.glob('*.tmp')))

    def test_scrapers_fail_when_table_missing_or_empty(self):
        for module, fetch_name, html in ((owners, 'fetch_owner_status', '<html></html>'),
                                         (owners, 'fetch_owner_status', '<table width="98%"><tr><td>Hull</td></tr></table>'),
                                         (sails, 'fetch_url', '<html></html>'),
                                         (sails, 'fetch_url', '<div class="pollText"></div><table><tr><th>Hull</th></tr></table>')):
            with self.subTest(module=module.__name__, html=html), \
                 patch.object(module, fetch_name, return_value=html), \
                 patch.object(module, 'save_json') as save:
                with self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
                save.assert_not_called()

    def test_tracker_roundtrip_preserves_dues_and_uses_current_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / f'payment_tracker_{YEAR}.csv'
            boats = [dict(BOAT, **{'Fleet Dues': 'Not Paid'}), dict(BOAT, **{'Hull Number': '2'})]
            tracker.create_payment_tracker(boats, path)
            tracker.update_payment_status(path, '1', paid=True)
            updated, count = manager.merge_with_tracker(boats, path)
            self.assertEqual(count, 1)
            self.assertTrue(all(b['Fleet Dues'] == 'Paid' for b in updated))
            self.assertEqual(set(updated[0]), set(BOAT))
            with self.assertRaises(FileExistsError):
                tracker.create_payment_tracker(boats, path)
            path.write_text('Hull,Paid 2000\n1,YES\n')
            with self.assertRaises(ValueError):
                manager.merge_with_tracker(boats, path)

    def test_tracker_no_does_not_clear_manual_payment(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'tracker.csv'
            path.write_text(f'Hull,Paid {YEAR}\n1,NO\n')
            result, _ = manager.merge_with_tracker([copy.deepcopy(BOAT)], path)
            self.assertEqual(result[0]['Fleet Dues'], 'Paid')

    def test_followup_uses_fleet_dues_not_class_membership(self):
        with tempfile.TemporaryDirectory() as temporary:
            unpaid, _ = generate_report([BOAT], [], Path(temporary) / 'report.txt')
            self.assertEqual(unpaid, [])
            unpaid, _ = generate_report([dict(BOAT, **{'Fleet Dues': 'Not Paid'})], [MEMBER], Path(temporary) / 'report.txt')
            self.assertEqual(len(unpaid), 1)

    def test_season_reset_backup_contains_original_paid_status(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'boats.json'
            path.write_text(json.dumps([BOAT]))
            original = path.read_bytes()
            reset_dues_season(str(path), reset_class_dues=False)
            backup = next(path.parent.glob('*_backup_*.json'))
            self.assertEqual(backup.read_bytes(), original)
            self.assertEqual(json.loads(path.read_text())[0]['Fleet Dues'], 'Not Paid')

    def test_conversion_preserves_simplified_payments_and_backs_up(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'boats.json'
            path.write_text(json.dumps([BOAT]))
            original = path.read_bytes()
            convert_to_simplified_format(str(path))
            self.assertEqual(json.loads(path.read_text()), [BOAT])
            self.assertEqual(next(path.parent.glob('*_backup_*.json')).read_bytes(), original)
            legacy = {'Hull Number': '1', 'Boat Name': 'Example', 'Yacht Club': 'EYC',
                      'Fleet Dues 2025': 'Paid', 'Class Dues 2025': 'Unpaid'}
            path.write_text(json.dumps([legacy]))
            convert_to_simplified_format(str(path))
            self.assertEqual(json.loads(path.read_text()), [BOAT])


class PipelineTests(unittest.TestCase):
    def seed(self, root):
        for relative, records in zip(pipeline.SOURCE_FILES, ([MEMBER], [SAIL], [BOAT])):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(records))

    def test_failed_refresh_does_not_publish_any_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.seed(root)
            originals = {p: p.read_bytes() for p in root.rglob('*.json')}
            with patch.object(pipeline, 'DATA_DIR', root), \
                 patch.object(pipeline.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'scrape')):
                with self.assertRaises(subprocess.CalledProcessError):
                    pipeline.main()
            self.assertTrue(all(path.read_bytes() == contents for path, contents in originals.items()))
            self.assertFalse((root / 'metadata.json').exists())

    def test_local_payment_edit_during_refresh_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.seed(root)
            edited = dict(BOAT, **{'Fleet Dues': 'Not Paid'})
            def edit_while_refreshing(*args, **kwargs):
                (root / 'boats/boats_fleet22.json').write_text(json.dumps([edited]))
            with patch.object(pipeline, 'DATA_DIR', root), \
                 patch.object(pipeline.subprocess, 'run', side_effect=edit_while_refreshing):
                with self.assertRaises(RuntimeError):
                    pipeline.main()
            self.assertEqual(json.loads((root / 'boats/boats_fleet22.json').read_text()), [edited])
            self.assertFalse((root / 'metadata.json').exists())

    def test_complete_refresh_builds_from_fresh_members_and_publishes_metadata(self):
        run = subprocess.run
        calls = []
        def offline_run(command, **kwargs):
            module = command[-1]
            calls.append(module)
            staged = Path(kwargs['env']['FLEET22_DATA_DIR'])
            if module.endswith('scrape_owner_status'):
                (staged / 'members/j105_members_status.json').write_text(json.dumps([dict(MEMBER, **{'Boat Name': 'Fresh name'})]))
            elif module.endswith('scrape_sail_tags'):
                (staged / 'sails/sail_tags.json').write_text(json.dumps([SAIL]))
            else:
                return run(command, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.seed(root)
            with patch.object(pipeline, 'DATA_DIR', root), patch.object(pipeline.subprocess, 'run', side_effect=offline_run):
                pipeline.main()
            result = json.loads((root / 'boats/boats_fleet22.json').read_text())[0]
            self.assertEqual(result['Boat Name'], 'Fresh name')
            self.assertEqual(result['Fleet Dues'], 'Paid')
            self.assertEqual(result['Class Dues'], 'Paid')
            metadata = json.loads((root / 'metadata.json').read_text())
            for relative, info in metadata['files'].items():
                self.assertEqual(info['sha256'], hashlib.sha256((root / relative).read_bytes()).hexdigest())
            self.assertLess(calls.index('scripts.scrapers.scrape_owner_status'), calls.index('scripts.scrapers.scrape_fleet_boats'))


if __name__ == '__main__':
    unittest.main()
