"""Master sheet list. Order here = order in the combined plan set PDF.
Sheets listed but not yet built are skipped by build.py (and flagged).
'BY OTHERS' sheets are prepared by the licensed engineer / energy consultant."""

SHEET_INDEX = [
    ("A0.0", "COVER SHEET & PROJECT DATA"),
    ("A0.1", "GENERAL NOTES & CALGREEN"),
    ("A1.0", "SITE PLAN"),
    ("A2.0", "FLOOR PLAN"),
    ("A3.0", "ROOF PLAN"),
    ("A4.0", "EXTERIOR ELEVATIONS"),
    ("A5.0", "BUILDING SECTIONS"),
    ("A6.0", "ARCHITECTURAL DETAILS"),
    ("E1.0", "ELECTRICAL PLAN"),
    ("P1.0", "PLUMBING & GAS PLAN"),
    ("M1.0", "MECHANICAL PLAN"),
    ("T24.1", "TITLE 24 ENERGY COMPLIANCE (BY OTHERS)"),
    ("S0.1", "STRUCTURAL GENERAL NOTES (BY OTHERS)"),
    ("S1.0", "FOUNDATION & ROOF FRAMING PLAN (BY OTHERS)"),
    ("S2.0", "STRUCTURAL DETAILS (BY OTHERS)"),
]
