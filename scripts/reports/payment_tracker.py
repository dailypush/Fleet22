#!/usr/bin/env python3
"""
Payment Tracker - Create and manage payment tracking CSV
Allows easy updating of payment status for Fleet 22 boats.
"""
import sys
import argparse
import csv
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import load_json
from utils.path_utils import PROJECT_ROOT

# Setup logging
logger = setup_logger('payment_tracker', PROJECT_ROOT / 'logs' / 'reports.log')

def create_payment_tracker(boats_data, output_file):
    """Create a CSV file for tracking payments."""
    try:
        logger.info(f"Creating payment tracker CSV: {output_file}")
        
        # Prepare data
        fieldnames = [
            'Hull',
            'Boat Name',
            'Yacht Club',
            'Paid 2025',
            'Payment Date',
            'Payment Method',
            'Amount',
            'Contact Email',
            'Notes'
        ]
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for boat in sorted(boats_data, key=lambda x: int(x.get('Hull Number', '0')) if x.get('Hull Number', '0').isdigit() else 0):
                writer.writerow({
                    'Hull': boat.get('Hull Number', ''),
                    'Boat Name': boat.get('Boat Name', ''),
                    'Yacht Club': boat.get('Yacht Club', ''),
                    'Paid 2025': 'NO',
                    'Payment Date': '',
                    'Payment Method': '',
                    'Amount': '',
                    'Contact Email': '',
                    'Notes': ''
                })
        
        logger.info(f"Payment tracker created with {len(boats_data)} boats")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating payment tracker: {e}")
        raise

def update_payment_status(tracker_file, hull, paid=True, payment_date=None, method=None, amount=150):
    """Update payment status for a specific boat."""
    try:
        logger.info(f"Updating payment status for hull {hull}")
        
        rows = []
        updated = False
        
        with open(tracker_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Hull'] == str(hull):
                    row['Paid 2025'] = 'YES' if paid else 'NO'
                    if payment_date:
                        row['Payment Date'] = payment_date
                    if method:
                        row['Payment Method'] = method
                    if paid and amount:
                        row['Amount'] = f"${amount}"
                    updated = True
                    logger.info(f"Updated hull {hull}: Paid={paid}")
                rows.append(row)
        
        if not updated:
            logger.warning(f"Hull {hull} not found in tracker")
            return False
        
        # Write back
        with open(tracker_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating payment status: {e}")
        raise

def generate_summary(tracker_file):
    """Generate summary statistics from tracker."""
    try:
        paid_count = 0
        unpaid_count = 0
        total_collected = 0
        paid_boats = []
        unpaid_boats = []
        
        with open(tracker_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Paid 2025'].upper() == 'YES':
                    paid_count += 1
                    paid_boats.append(row)
                    # Extract amount
                    amount_str = row.get('Amount', '').replace('$', '').replace(',', '')
                    if amount_str:
                        try:
                            total_collected += float(amount_str)
                        except ValueError:
                            pass
                else:
                    unpaid_count += 1
                    unpaid_boats.append(row)
        
        total = paid_count + unpaid_count
        payment_rate = (paid_count / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 80)
        print("FLEET 22 PAYMENT TRACKER SUMMARY")
        print("=" * 80)
        print(f"Total Boats:       {total}")
        print(f"Paid:              {paid_count} ({payment_rate:.1f}%)")
        print(f"Unpaid:            {unpaid_count} ({100-payment_rate:.1f}%)")
        print(f"Total Collected:   ${total_collected:,.2f}")
        print(f"Outstanding:       ${unpaid_count * 150:,.2f} (est.)")
        print()
        
        if unpaid_boats:
            print("\nUNPAID BOATS:")
            print("-" * 80)
            for boat in unpaid_boats:
                print(f"  Hull {boat['Hull']:>4} | {boat['Boat Name']:<30} | {boat['Yacht Club']:<10}")
        
        return {
            'total': total,
            'paid': paid_count,
            'unpaid': unpaid_count,
            'collected': total_collected,
            'rate': payment_rate
        }
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Payment tracker for Fleet 22 boats"
    )
    parser.add_argument(
        'action',
        choices=['create', 'update', 'summary'],
        help="Action to perform"
    )
    parser.add_argument(
        '--boats',
        type=Path,
        default=PROJECT_ROOT / 'data' / 'boats' / 'boats_fleet22.json',
        help="Path to boats data JSON file"
    )
    parser.add_argument(
        '--tracker',
        type=Path,
        default=PROJECT_ROOT / 'data' / 'payments' / 'payment_tracker_2025.csv',
        help="Path to payment tracker CSV file"
    )
    parser.add_argument(
        '--hull',
        type=str,
        help="Hull number to update (for 'update' action)"
    )
    parser.add_argument(
        '--paid',
        action='store_true',
        help="Mark as paid (for 'update' action)"
    )
    parser.add_argument(
        '--date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help="Payment date (YYYY-MM-DD)"
    )
    parser.add_argument(
        '--method',
        type=str,
        choices=['Venmo', 'Check', 'Cash', 'Online', 'Other'],
        help="Payment method"
    )
    parser.add_argument(
        '--amount',
        type=float,
        default=150,
        help="Payment amount (default: 150)"
    )
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting payment tracker action: {args.action}")
        
        if args.action == 'create':
            boats_data = load_json(args.boats)
            output_path = create_payment_tracker(boats_data, args.tracker)
            print(f"✅ Payment tracker created: {output_path}")
            print(f"📝 Track payments by editing this CSV file")
            print(f"   Or use: python {Path(__file__).name} update --hull <number> --paid")
            
        elif args.action == 'update':
            if not args.hull:
                print("❌ Error: --hull required for update action")
                return 1
            
            if not args.tracker.exists():
                print(f"❌ Error: Tracker file not found: {args.tracker}")
                print(f"   Create it first: python {Path(__file__).name} create")
                return 1
            
            success = update_payment_status(
                args.tracker,
                args.hull,
                paid=args.paid,
                payment_date=args.date,
                method=args.method,
                amount=args.amount
            )
            
            if success:
                print(f"✅ Updated hull {args.hull}: Paid = {args.paid}")
                generate_summary(args.tracker)
            else:
                print(f"❌ Hull {args.hull} not found in tracker")
                return 1
                
        elif args.action == 'summary':
            if not args.tracker.exists():
                print(f"❌ Error: Tracker file not found: {args.tracker}")
                return 1
            
            generate_summary(args.tracker)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during payment tracking: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
