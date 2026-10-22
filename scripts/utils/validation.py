"""Validate full source datasets before replacing the last good snapshot."""
SCHEMAS = {
    "boats": ("Hull Number", {"Hull Number", "Boat Name", "Yacht Club", "Fleet Dues", "Class Dues"}),
    "members": ("Hull", {"Hull", "Owners/Helmsmen", "Status", "Boat Name", "Fleet", "Class Membership"}),
    "sails": ("Hull", {"Hull", "Purchaser", "Certificate No.", "Sailmaker", "Delivery Date", "Sail Type", "Fleet", "Notes"}),
}


def validate_records(data, kind):
    hull_key, fields = SCHEMAS[kind]
    if not isinstance(data, list) or not data:
        raise ValueError(f"{kind}: expected a nonempty list")
    seen = set()
    for index, row in enumerate(data):
        if not isinstance(row, dict) or not fields.issubset(row):
            raise ValueError(f"{kind} record {index}: missing required fields")
        if any(not isinstance(row[key], str) for key in fields):
            raise ValueError(f"{kind} record {index}: fields must be strings")
        hull = row[hull_key]
        if not hull.isdigit():
            raise ValueError(f"{kind} record {index}: invalid hull number")
        if kind == "boats":
            if hull in seen:
                raise ValueError(f"boats: duplicate hull {hull}")
            if any(row[key] not in {"Paid", "Not Paid"} for key in ("Fleet Dues", "Class Dues")):
                raise ValueError(f"boats: invalid dues value for hull {hull}")
            if any(key.startswith(("Fleet Dues ", "Class Dues ")) for key in row):
                raise ValueError("boats: legacy dues fields are not supported")
        if kind == "sails" and not row["Certificate No."].strip():
            raise ValueError(f"sails record {index}: missing certificate number")
        seen.add(hull)


def validate_update(data, previous, kind):
    validate_records(data, kind)
    if previous is None:
        return
    validate_records(previous, kind)
    if len(data) < len(previous) * 0.8:
        raise ValueError(f"{kind}: record count fell from {len(previous)} to {len(data)} (over 20%)")
    hull_key = SCHEMAS[kind][0]
    old_hulls = {r[hull_key] for r in previous}
    new_hulls = {r[hull_key] for r in data}
    if len(old_hulls & new_hulls) < len(old_hulls) * 0.8:
        raise ValueError(f"{kind}: more than 20% of existing hulls disappeared")
