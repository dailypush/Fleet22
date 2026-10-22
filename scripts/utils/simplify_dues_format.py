#!/usr/bin/env python3
"""
Convert detailed fleet dues format to simplified format.
This script converts the year-specific dues format to a simple Paid/Not Paid format
that is easier to maintain and reset each season.
"""

import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.data_loader import load_json, save_json
from utils.path_utils import BOATS_FILE
from utils.validation import validate_records


def dues_value(boat, field):
    if field in boat:
        if boat[field] not in {'Paid', 'Not Paid'}:
            raise ValueError(f'Invalid {field} value')
        return boat[field]
    legacy = sorted((key for key in boat if re.fullmatch(re.escape(field) + r' \d{4}', key)), reverse=True)
    if not legacy:
        return 'Not Paid'
    return 'Paid' if boat[legacy[0]] == 'Paid' else 'Not Paid'


def convert_to_simplified_format(input_file: str, output_file: str = None):
    """
    Convert detailed dues format to simplified format.
    
    Detailed format:
        "Fleet Dues 2025": "Paid"/"Unpaid"
        "Fleet Dues Payment Date": "2025-09-22"
        "Fleet Dues Payment Method": "Check"
        "Class Dues 2025": "Paid"/"Unpaid"
        "Class Dues Payment Date": "2025-01-01"
    
    Simplified format:
        "Fleet Dues": "Paid"/"Not Paid"
        "Class Dues": "Paid"/"Not Paid"
    """
    
    # Read the input file
    data = load_json(Path(input_file))
    
    # Convert each boat entry
    simplified_data = []
    for boat in data:
        simplified_boat = {
            "Hull Number": boat.get("Hull Number", ""),
            "Boat Name": boat.get("Boat Name", ""),
            "Yacht Club": boat.get("Yacht Club", ""),
            "Fleet Dues": dues_value(boat, "Fleet Dues"),
            "Class Dues": dues_value(boat, "Class Dues")
        }
        simplified_data.append(simplified_boat)
    
    # Determine output file
    if output_file is None:
        output_file = input_file
    
    # Write the simplified data
    validate_records(simplified_data, 'boats')
    save_json(simplified_data, Path(output_file))
    
    print(f"✅ Converted {len(simplified_data)} boat entries to simplified format")
    print(f"📁 Output written to: {output_file}")
    
    # Print summary statistics
    fleet_paid = sum(1 for b in simplified_data if b["Fleet Dues"] == "Paid")
    class_paid = sum(1 for b in simplified_data if b["Class Dues"] == "Paid")
    
    print(f"\n📊 Summary:")
    print(f"   Fleet Dues Paid: {fleet_paid}/{len(simplified_data)}")
    print(f"   Class Dues Paid: {class_paid}/{len(simplified_data)}")

if __name__ == "__main__":
    # Default paths
    input_file = BOATS_FILE
    
    # Allow command-line override
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        sys.exit(1)
    
    convert_to_simplified_format(str(input_file), output_file)
