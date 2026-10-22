"""Shared season and co-owner rules for class membership.

Only a full Member for the selected season satisfies boat Class Dues.
Associate membership alone does not; any co-owner's full membership does.
"""
import re
from datetime import date


def membership_parts(status):
    match = re.fullmatch(r"(Member|Associate) (\d{4})", str(status).strip())
    return (match[1], int(match[2])) if match else ("", 0)


def is_paid_membership(status, season=None):
    kind, year = membership_parts(status)
    return kind == "Member" and year == int(season or date.today().year)


def membership_rank(status, season=None):
    kind, year = membership_parts(status)
    return (is_paid_membership(status, season), year, kind == "Member")


def members_by_hull(records):
    grouped = {}
    for record in records:
        grouped.setdefault(str(record["Hull"]).strip(), []).append(record)
    return grouped


def best_membership(records, season=None):
    return max((r.get("Class Membership", "") for r in records),
               key=lambda status: membership_rank(status, season), default="")


def primary_member(records, season=None):
    """Prefer an owner over crew/associates, then current/recent membership.

    A stable name tie-break makes output independent of source row ordering.
    """
    return max(records, key=lambda r: (
        r.get("Status") == "OW",
        membership_rank(r.get("Class Membership", ""), season),
        r.get("Owners/Helmsmen", ""),
    ))
