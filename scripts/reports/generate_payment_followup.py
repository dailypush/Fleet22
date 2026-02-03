#!/usr/bin/env python3
"""
Payment Follow-up Report Generator for Fleet22_us repository
Generates detailed payment follow-up reports with contact information and yacht club breakdown.
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.data_loader import load_json
from utils.path_utils import PROJECT_ROOT

# Setup logging
logger = setup_logger('payment_followup', PROJECT_ROOT / 'logs' / 'reports.log')

def load_boats_data(file_path):
    """Load boats data from JSON file."""
    try:
        logger.info(f"Loading boats data from {file_path}")
        boats = load_json(file_path)
        logger.info(f"Loaded {len(boats)} boats")
        return boats
    except Exception as e:
        logger.error(f"Error loading boats data: {e}")
        raise

def load_members_data(file_path):
    """Load members status data from JSON file."""
    try:
        logger.info(f"Loading members data from {file_path}")
        members = load_json(file_path)
        logger.info(f"Loaded {len(members)} member records")
        return members
    except Exception as e:
        logger.error(f"Error loading members data: {e}")
        raise

def get_payment_status(members_data):
    """Extract payment status from members data."""
    paid_members = set()
    for member in members_data:
        # Check if member has paid (status == 'Active' or similar)
        if member.get('status') == 'Active' or member.get('paid', False):
            # Extract hull number or boat name
            if 'hull' in member:
                paid_members.add(str(member['hull']))
            elif 'boat' in member:
                paid_members.add(member['boat'])
    return paid_members

def categorize_boats(boats_data, paid_members):
    """Categorize boats into paid and unpaid."""
    paid_boats = []
    unpaid_boats = []
    
    for boat in boats_data:
        hull = str(boat.get('Hull Number', ''))
        boat_name = boat.get('Boat Name', 'Unknown')
        yacht_club = boat.get('Yacht Club', 'Unknown')
        
        boat_info = {
            'hull': hull,
            'name': boat_name,
            'club': yacht_club
        }
        
        # Check if boat is in paid members (by hull or name)
        if hull in paid_members or boat_name in paid_members:
            paid_boats.append(boat_info)
        else:
            unpaid_boats.append(boat_info)
    
    return paid_boats, unpaid_boats

def generate_club_breakdown(unpaid_boats):
    """Generate breakdown by yacht club."""
    club_breakdown = defaultdict(list)
    for boat in unpaid_boats:
        club_breakdown[boat['club']].append(boat)
    return dict(club_breakdown)

def generate_report(boats_data, members_data, output_file=None):
    """Generate comprehensive payment follow-up report."""
    try:
        logger.info("Generating payment follow-up report...")
        
        # Get payment status
        paid_members = get_payment_status(members_data)
        
        # Categorize boats
        paid_boats, unpaid_boats = categorize_boats(boats_data, paid_members)
        
        # Calculate statistics
        total_boats = len(boats_data)
        paid_count = len(paid_boats)
        unpaid_count = len(unpaid_boats)
        payment_rate = (paid_count / total_boats * 100) if total_boats > 0 else 0
        
        # Generate club breakdown
        club_breakdown = generate_club_breakdown(unpaid_boats)
        
        # Build report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("FLEET 22 PAYMENT FOLLOW-UP REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Fleet Boats:     {total_boats}")
        report_lines.append(f"Paid Boats:            {paid_count} ({payment_rate:.1f}%)")
        report_lines.append(f"Unpaid Boats:          {unpaid_count} ({100-payment_rate:.1f}%)")
        report_lines.append(f"Outstanding Revenue:   ${unpaid_count * 150:,} (est. $150/boat)")
        report_lines.append("")
        
        # Unpaid Boats by Yacht Club
        report_lines.append("UNPAID BOATS BY YACHT CLUB")
        report_lines.append("-" * 80)
        for club, boats in sorted(club_breakdown.items()):
            report_lines.append(f"\n{club} ({len(boats)} boat{'s' if len(boats) != 1 else ''})")
            report_lines.append("  " + "-" * 76)
            for boat in sorted(boats, key=lambda x: x['hull']):
                report_lines.append(f"  Hull {boat['hull']:>4} | {boat['name']:<30}")
        report_lines.append("")
        
        # Complete Unpaid List (for easy copy/paste)
        report_lines.append("\nUNPAID BOATS - COMPLETE LIST")
        report_lines.append("-" * 80)
        report_lines.append(f"{'Hull':<6} | {'Boat Name':<30} | {'Yacht Club':<10}")
        report_lines.append("-" * 80)
        for boat in sorted(unpaid_boats, key=lambda x: int(x['hull']) if x['hull'].isdigit() else 0):
            report_lines.append(f"{boat['hull']:<6} | {boat['name']:<30} | {boat['club']:<10}")
        report_lines.append("")
        
        # Action Items
        report_lines.append("\nRECOMMENDED ACTION ITEMS")
        report_lines.append("-" * 80)
        report_lines.append("1. Send reminder emails to yacht club contacts for unpaid boats")
        report_lines.append("2. Follow up with clubs having multiple unpaid boats")
        report_lines.append(f"3. Set deadline for payment: {datetime.now().strftime('%B %d, %Y')} + 30 days")
        report_lines.append("4. Consider late fee policy for boats unpaid after deadline")
        report_lines.append("5. Verify membership status with yacht club secretaries")
        report_lines.append("")
        
        # Contact Information Template
        report_lines.append("\nEMAIL TEMPLATE FOR FOLLOW-UP")
        report_lines.append("-" * 80)
        report_lines.append("""
Subject: Fleet 22 Dues Payment Reminder - [Yacht Club Name]

Dear [Yacht Club Fleet Captain/Secretary],

This is a friendly reminder that the following Fleet 22 boats from [Yacht Club]
have outstanding dues payments for the 2026 season:

[List boats here]

Annual fleet dues are $150 per boat and help support:
- Fleet website and member resources
- Regatta organization and coordination
- Class rules and certification
- Communication and member services

Payment can be made via:
- Venmo: @fleet22lakerie
- Check: Fleet 22, c/o Treasurer
- Online: https://fleet22.us/fleetdues.html

Please forward this to your members or let us know if you need assistance
reaching these boat owners.

Thank you for your support of Fleet 22!

Best regards,
Fleet 22 Lake Erie
fleet22@fleet22.us
""")
        
        # Generate report text
        report_text = "\n".join(report_lines)
        
        # Output to file or console
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_text)
            logger.info(f"Report saved to {output_path}")
            print(f"✅ Report saved to {output_path}")
        else:
            print(report_text)
        
        # Summary
        print(f"\n📊 Summary: {unpaid_count} unpaid boats across {len(club_breakdown)} yacht clubs")
        print(f"💰 Outstanding: ${unpaid_count * 150:,} (estimated)")
        
        logger.info(f"Report generation completed. {unpaid_count} unpaid boats identified.")
        return unpaid_boats, club_breakdown
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Generate payment follow-up report for Fleet 22 boats"
    )
    parser.add_argument(
        '--boats',
        type=Path,
        default=PROJECT_ROOT / 'data' / 'boats' / 'boats_fleet22.json',
        help="Path to boats data JSON file"
    )
    parser.add_argument(
        '--members',
        type=Path,
        default=PROJECT_ROOT / 'data' / 'members' / 'j105_members_status.json',
        help="Path to members status JSON file"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=PROJECT_ROOT / 'data' / 'payments' / 'payment_followup_report.txt',
        help="Output file path for the report"
    )
    parser.add_argument(
        '--club',
        type=str,
        help="Filter by specific yacht club (e.g., BYC, BHSC, NCYC)"
    )
    args = parser.parse_args()
    
    try:
        logger.info("Starting payment follow-up report generation...")
        
        # Load data
        boats_data = load_boats_data(args.boats)
        members_data = load_members_data(args.members)
        
        # Filter by club if specified
        if args.club:
            boats_data = [b for b in boats_data if b.get('Yacht Club') == args.club]
            logger.info(f"Filtered to {len(boats_data)} boats from {args.club}")
        
        # Generate report
        unpaid_boats, club_breakdown = generate_report(boats_data, members_data, args.output)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during report generation: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
