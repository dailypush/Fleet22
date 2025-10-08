#!/usr/bin/env python3
"""
Reset all fleet dues to 'Not Paid' at the start of a new sailing season.
This script resets both Fleet Dues and Class Dues for all boats.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def reset_dues_season(input_file: str, output_file: str = None, reset_class_dues: bool = True):
    """
    Reset all dues to 'Not Paid' for a new season.
    
    Args:
        input_file: Path to the boats_fleet22.json file
        output_file: Optional output path (defaults to input_file)
        reset_class_dues: Whether to also reset class dues (default: True)
    """
    
    # Read the input file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Reset dues for each boat
    reset_count = 0
    for boat in data:
        # Always reset Fleet Dues
        if boat.get("Fleet Dues") != "Not Paid":
            boat["Fleet Dues"] = "Not Paid"
            reset_count += 1
        
        # Optionally reset Class Dues
        if reset_class_dues and boat.get("Class Dues") != "Not Paid":
            boat["Class Dues"] = "Not Paid"
            reset_count += 1
    
    # Determine output file
    if output_file is None:
        output_file = input_file
    
    # Create backup before overwriting
    if output_file == input_file:
        backup_file = Path(input_file).parent / f"boats_fleet22_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"📁 Backup created: {backup_file}")
    
    # Write the reset data
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"✅ Reset dues for {len(data)} boats")
    print(f"📁 Output written to: {output_file}")
    
    # Print summary
    fleet_reset = sum(1 for b in data if b.get("Fleet Dues") == "Not Paid")
    class_reset = sum(1 for b in data if b.get("Class Dues") == "Not Paid")
    
    print(f"\n📊 Season Reset Summary:")
    print(f"   All Fleet Dues: Not Paid ({fleet_reset}/{len(data)})")
    if reset_class_dues:
        print(f"   All Class Dues: Not Paid ({class_reset}/{len(data)})")
    else:
        print(f"   Class Dues: Preserved")

def main():
    """Main execution function."""
    # Default paths
    project_root = Path(__file__).parent.parent.parent
    boats_file = project_root / "data" / "boats" / "boats_fleet22.json"
    root_file = project_root / "data" / "boats_fleet22.json"
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Reset fleet dues for a new sailing season',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Reset both Fleet and Class Dues
  python3 scripts/utils/reset_dues_season.py
  
  # Reset only Fleet Dues (preserve Class Dues)
  python3 scripts/utils/reset_dues_season.py --fleet-only
  
  # Specify custom input file
  python3 scripts/utils/reset_dues_season.py --input /path/to/boats.json
        '''
    )
    parser.add_argument('--input', '-i', 
                       help='Input file path (default: data/boats/boats_fleet22.json)',
                       default=str(boats_file))
    parser.add_argument('--output', '-o',
                       help='Output file path (default: same as input)')
    parser.add_argument('--fleet-only', 
                       action='store_true',
                       help='Reset only Fleet Dues, preserve Class Dues')
    parser.add_argument('--yes', '-y',
                       action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Load data to check current status
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    fleet_paid = sum(1 for b in data if b.get("Fleet Dues") == "Paid")
    class_paid = sum(1 for b in data if b.get("Class Dues") == "Paid")
    
    # Confirmation prompt
    if not args.yes:
        print(f"\n⚠️  WARNING: This will reset dues for {len(data)} boats")
        print(f"\nCurrent Status:")
        print(f"   Fleet Dues Paid: {fleet_paid}/{len(data)}")
        print(f"   Class Dues Paid: {class_paid}/{len(data)}")
        print(f"\nAfter Reset:")
        print(f"   Fleet Dues Paid: 0/{len(data)}")
        if args.fleet_only:
            print(f"   Class Dues Paid: {class_paid}/{len(data)} (preserved)")
        else:
            print(f"   Class Dues Paid: 0/{len(data)}")
        
        confirm = input(f"\nContinue? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Operation cancelled")
            sys.exit(0)
    
    # Perform reset
    reset_dues_season(
        str(input_file), 
        args.output,
        reset_class_dues=not args.fleet_only
    )
    
    # Also update the root file if we updated the boats directory file
    if str(input_file) == str(boats_file) and root_file.exists():
        print(f"\n🔄 Also updating root file: {root_file}")
        reset_dues_season(
            str(root_file), 
            None,
            reset_class_dues=not args.fleet_only
        )
    
    print("\n✅ Season reset complete!")
    print("\n💡 Next steps:")
    print("   1. Update Fleet Dues to 'Paid' as payments arrive")
    print("   2. Run update_payment_status.py to sync Class Dues from membership data")
    print("   3. Commit and push changes to update the website")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
