"""A0.1 - General notes & CALGreen residential mandatory measures (2025 CGBSC Ch. 4 & 7)."""
import math

from ezdxf.enums import TextEntityAlignment

from plans.lib import new_sheet, north_arrow, rect, text
from plans.textblocks import header, para

NUMBER, TITLE = "A0.1", "GENERAL NOTES & CALGREEN"

GENERAL = [
    "1. ALL WORK SHALL COMPLY WITH THE 2025 CALIFORNIA BUILDING STANDARDS CODE (TITLE 24) AND COUNTY OF ORANGE "
    "ORDINANCES. WHERE CONFLICTS OCCUR, THE MOST RESTRICTIVE SHALL GOVERN.",
    "2. CONTRACTOR SHALL VERIFY ALL DIMENSIONS, PROPERTY LINES, UTILITIES AND SITE CONDITIONS BEFORE STARTING WORK "
    "AND REPORT ANY DISCREPANCY TO THE DESIGNER. DO NOT SCALE DRAWINGS; WRITTEN DIMENSIONS GOVERN.",
    "3. DIMENSIONS ARE TO FACE OF STUD / FACE OF CONCRETE UNLESS NOTED OTHERWISE.",
    "4. STRUCTURAL WORK SHALL BE PER THE STAMPED STRUCTURAL DRAWINGS AND CALCULATIONS. FOUNDATION DESIGN SHALL "
    "FOLLOW THE RECOMMENDATIONS OF THE SOILS REPORT (SITE IS IN A STATE LIQUEFACTION HAZARD ZONE).",
    "5. APPROVED PLANS AND PERMIT CARD SHALL BE KEPT ON SITE AND AVAILABLE TO THE INSPECTOR AT ALL TIMES.",
    "6. CONSTRUCTION HOURS PER COUNTY NOISE ORDINANCE: 7:00 AM - 8:00 PM MONDAY THROUGH SATURDAY. NO WORK ON "
    "SUNDAYS OR FEDERAL HOLIDAYS.",
    "7. CALL DIG ALERT (811) AT LEAST 2 WORKING DAYS BEFORE ANY EXCAVATION (GOV. CODE 4216).",
    "8. SMOKE ALARMS (CRC R314) IN EACH SLEEPING ROOM, OUTSIDE EACH SLEEPING AREA AND ON EACH STORY; "
    "CARBON MONOXIDE ALARMS (CRC R315) OUTSIDE SLEEPING AREAS. HARDWIRED, INTERCONNECTED, WITH BATTERY BACKUP.",
    "9. EMERGENCY ESCAPE OPENINGS (CRC R310) IN EACH BEDROOM: NET CLEAR OPENING 5.7 SF MIN. (5.0 SF AT GRADE "
    "FLOOR), 24\" MIN. CLEAR HEIGHT, 20\" MIN. CLEAR WIDTH, SILL 44\" MAX. ABOVE FLOOR.",
    "10. SAFETY GLAZING (CRC R308) AT DOORS, SHOWER/TUB ENCLOSURES, WITHIN 24\" OF DOOR EDGES AND WHERE "
    "OTHERWISE REQUIRED.",
    "11. SHOWER WALLS: NON-ABSORBENT SURFACE TO 72\" MIN. ABOVE DRAIN (CRC R307.2). SHOWER VALVES: PRESSURE-"
    "BALANCE OR THERMOSTATIC MIXING, 120 DEG F MAX. (CPC 408.3).",
    "12. WATER HEATER SHALL BE STRAPPED AT UPPER AND LOWER 1/3 OF TANK (CPC 507.2) WITH T&P RELIEF DISCHARGE "
    "TO AN APPROVED LOCATION.",
    "13. PROVIDE 1-HR FIRE-RESISTIVE CONSTRUCTION FOR WALLS AND EAVE PROJECTIONS WHERE FIRE SEPARATION "
    "DISTANCE IS LESS THAN 5 FT (CRC TABLE R302.1(1)). SEE SITE PLAN AND DETAILS.",
    "14. ATTIC VENTILATION PER CRC R806; ATTIC ACCESS 22\" x 30\" MIN. (CRC R807).",
]

SITE = [
    "1. GRADE SHALL FALL MIN. 6\" WITHIN THE FIRST 10 FT AWAY FROM THE FOUNDATION; IMPERVIOUS SURFACES MIN. 2% "
    "SLOPE. PROVIDE SWALES OR DRAINS WHERE 10 FT IS NOT AVAILABLE (CRC R401.3).",
    "2. NO DISCHARGE OF SOIL, CONSTRUCTION DEBRIS, WASTEWATER OR OTHER POLLUTANTS TO THE STREET, GUTTER OR "
    "STORM DRAIN. KEEP STOCKPILES COVERED AND STABILIZED.",
    "3. REFUSE BINS SHALL BE COVERED AT NIGHT AND DURING WIND OR RAIN. DEBRIS SHALL BE HAULED AWAY AND THE SITE "
    "LEFT BROOM-CLEAN.",
    "4. MAINTAIN 5 FT CLEAR ACCESS TO ALL UTILITY METERS, VALVES AND EQUIPMENT. NO CONSTRUCTION WITHIN 10 FT OF "
    "OVERHEAD POWER LINES.",
    "5. ALL NEW ON-SITE UTILITY LINES TO THE ADU SHALL BE INSTALLED UNDERGROUND.",
    "6. METER ALTERATIONS / RELOCATIONS SHALL BE COORDINATED WITH THE SERVING UTILITY AND APPROVED BY THE "
    "BUILDING INSPECTOR BEFORE INSTALLATION.",
]

CALGREEN_A = [
    "\\LPLANNING & DESIGN\\l",
    "4.106.2 STORM WATER: PROJECTS < 1 ACRE SHALL PREVENT POLLUTION DURING CONSTRUCTION WITH BMPs (RETENTION "
    "BASINS, DIVERSION TO A FILTER, OR LOCAL ORDINANCE COMPLIANCE).",
    "4.106.3 GRADING & PAVING: SITE SHALL BE GRADED TO KEEP SURFACE WATER FROM ENTERING BUILDINGS.",
    "4.106.4 EV CHARGING: NOT REQUIRED - ADU WITHOUT ADDITIONAL PARKING FACILITIES (EXCEPTION).",
    "\\LENERGY EFFICIENCY\\l",
    "4.201.1 BUILDING SHALL MEET OR EXCEED THE 2025 CALIFORNIA ENERGY CODE. SEE TITLE 24 SHEETS.",
    "\\LWATER EFFICIENCY\\l",
    "4.303.1 PLUMBING FIXTURES (MAX. FLOW): WATER CLOSETS 1.28 GPF; SHOWERHEADS 1.8 GPM @ 80 PSI; LAVATORY "
    "FAUCETS 1.2 GPM @ 60 PSI; KITCHEN FAUCETS 1.8 GPM @ 60 PSI.",
    "4.303.2 FIXTURES SHALL MEET CPC STANDARDS.",
    "4.304.1 OUTDOOR WATER USE: NEW LANDSCAPE OF 500 SF OR MORE SHALL COMPLY WITH MWELO.",
    "\\LMATERIAL CONSERVATION\\l",
    "4.406.1 RODENT PROOFING: SEAL ANNULAR SPACES AROUND PIPES, CABLES, CONDUITS AND OPENINGS IN SOLE/BOTTOM "
    "PLATES WITH CEMENT MORTAR, CONCRETE MASONRY OR SIMILAR.",
    "4.408.1 CONSTRUCTION WASTE: RECYCLE AND/OR SALVAGE MIN. 65% OF NON-HAZARDOUS CONSTRUCTION AND "
    "DEMOLITION WASTE; PROVIDE DOCUMENTATION TO THE INSPECTOR.",
    "4.410.1 OPERATION & MAINTENANCE MANUAL SHALL BE PROVIDED TO THE OWNER / OCCUPANT AT FINAL INSPECTION.",
]

CALGREEN_B = [
    "\\LENVIRONMENTAL QUALITY\\l",
    "4.503.1 FIREPLACES: NONE PROPOSED. ANY GAS FIREPLACE SHALL BE DIRECT-VENT, SEALED-COMBUSTION.",
    "4.504.1 DUCT OPENINGS AND HVAC EQUIPMENT SHALL BE COVERED DURING CONSTRUCTION.",
    "4.504.2.1-3 ADHESIVES, SEALANTS, CAULKS, PAINTS, COATINGS AND AEROSOL PAINTS SHALL MEET VOC LIMITS OF "
    "SCAQMD RULE 1168 / CARB SCM AND CALGREEN TABLES 4.504.1-4.504.3.",
    "4.504.2.4 VERIFICATION OF VOC COMPLIANCE SHALL BE PROVIDED TO THE INSPECTOR.",
    "4.504.3 CARPET SYSTEMS SHALL MEET CRI GREEN LABEL PLUS OR EQUIVALENT.",
    "4.504.4 MIN. 80% OF RESILIENT FLOORING SHALL MEET VOC EMISSION REQUIREMENTS.",
    "4.504.5 COMPOSITE WOOD PRODUCTS SHALL MEET CARB FORMALDEHYDE LIMITS (TABLE 4.504.5).",
    "4.505.2 CONCRETE SLAB: CAPILLARY BREAK - 4\" BASE OF 1/2\" OR LARGER CLEAN AGGREGATE WITH VAPOR RETARDER, "
    "OR AS DESIGNED BY THE ENGINEER / SOILS REPORT.",
    "4.505.3 FRAMING MOISTURE CONTENT SHALL NOT EXCEED 19% BEFORE ENCLOSURE; VERIFY WITH MOISTURE METER.",
    "4.506.1 BATHROOM EXHAUST FANS: ENERGY STAR, DUCTED TO OUTSIDE, WITH HUMIDITY CONTROL ADJUSTABLE 50%-80% "
    "(UNLESS FAN RUNS CONTINUOUSLY).",
    "4.507.2 HVAC SIZING: HEAT LOSS/GAIN PER ACCA MANUAL J, DUCTS PER MANUAL D, EQUIPMENT PER MANUAL S.",
    "\\LINSTALLER & SPECIAL INSPECTOR QUALIFICATIONS\\l",
    "702.1 HVAC INSTALLERS SHALL BE TRAINED / CERTIFIED IN THE INSTALLATION OF THE SYSTEMS INSTALLED.",
    "702.2 SPECIAL INSPECTORS SHALL BE QUALIFIED AND APPROVED BY THE ENFORCING AGENCY.",
    "703.1 DOCUMENTATION OF COMPLIANCE SHALL BE PROVIDED AS REQUIRED BY THE ENFORCING AGENCY.",
]


def build():
    s = new_sheet(NUMBER, TITLE)
    msp = s.msp
    xa, ya, xb, yb = s.drawing_area
    top = yb - 0.3
    gap = 0.3
    w = (xb - xa - 0.4 - 2 * gap) / 3
    c1, c2, c3 = xa + 0.2, xa + 0.2 + w + gap, xa + 0.2 + 2 * (w + gap)

    y = header(msp, c1, top, w, "GENERAL NOTES")
    y = para(msp, c1, y, GENERAL, w)
    y = header(msp, c2, top, w, "SITE & STORM WATER NOTES")
    y = para(msp, c2, y, SITE, w)
    y = header(msp, c2, y - 0.2, w, "CALGREEN MANDATORY MEASURES - RESIDENTIAL (1 OF 2)")
    y = para(msp, c2, y, CALGREEN_A, w)
    y = header(msp, c3, top, w, "CALGREEN MANDATORY MEASURES - RESIDENTIAL (2 OF 2)")
    y3 = para(msp, c3, y, CALGREEN_B, w)

    # ---- abbreviations (col 1, two sub-columns)
    y = header(msp, c1, ya + 8.4, w, "ABBREVIATIONS")
    half = (len(ABBR) + 1) // 2
    for i, (a, d) in enumerate(ABBR):
        cx = c1 + 0.1 + (w / 2 if i >= half else 0)
        cy = y - (i % half) * 0.24
        text(msp, a, (cx, cy), h=0.12)
        text(msp, d, (cx + 0.75, cy), h=0.12)

    # ---- symbol legend (cols 2-3)
    lx = c2
    lw = 2 * w + gap
    y = header(msp, lx, ya + 6.2, lw, "SYMBOL LEGEND")
    symbols(msp, lx, y, lw)
    return s


ABBR = [
    ("A.F.F.", "ABOVE FINISH FLOOR"), ("BLDG", "BUILDING"), ("C/L", "CENTERLINE"), ("CLG", "CEILING"),
    ("CLR", "CLEAR"), ("CO", "CARBON MONOXIDE"), ("CONC", "CONCRETE"), ("D/W", "DISHWASHER / WASHER-DRYER"),
    ("(E)", "EXISTING"), ("EQ", "EQUAL"), ("EXT", "EXTERIOR"), ("F.S.D.", "FIRE SEPARATION DISTANCE"),
    ("FIN", "FINISH"), ("FLR", "FLOOR"), ("FTG", "FOOTING"), ("GYP BD", "GYPSUM BOARD"),
    ("HDR", "HEADER"), ("HP", "HEAT PUMP"), ("INT", "INTERIOR"), ("MAX", "MAXIMUM"),
    ("MIN", "MINIMUM"), ("(N)", "NEW"), ("N.T.S.", "NOT TO SCALE"), ("O.C.", "ON CENTER"),
    ("P/L", "PROPERTY LINE"), ("PV", "PHOTOVOLTAIC"), ("REF", "REFRIGERATOR"), ("S.A.D.", "SEE ARCH. DRAWINGS"),
    ("S.S.D.", "SEE STRUCT. DRAWINGS"), ("SF", "SQUARE FEET"), ("SL", "SLIDING DOOR"), ("T.O.P.", "TOP OF PLATE"),
    ("TYP", "TYPICAL"), ("U.N.O.", "UNLESS NOTED OTHERWISE"), ("V.I.F.", "VERIFY IN FIELD"), ("W.I.C.", "WALK-IN CLOSET"),
    ("W/", "WITH"), ("WH", "WATER HEATER"),
]


def symbols(msp, x, y, w):
    """Draw common plan symbols with descriptions in a grid (paper inches)."""
    items = [
        ("PROPERTY LINE", "pl"), ("SETBACK LINE", "sb"), ("(N) WALL", "nw"), ("(E) TO BE REMOVED", "dm"),
        ("DOOR TAG (WIDTH-HEIGHT)", "dt"), ("WINDOW TAG", "wt"), ("KEYNOTE", "kn"), ("DETAIL / SECTION CALLOUT", "dc"),
        ("ELEVATION MARKER", "em"), ("SPOT ELEVATION", "se"), ("DRAINAGE FLOW & SLOPE", "df"), ("NORTH ARROW", "na"),
        ("SMOKE ALARM", "sa"), ("CARBON MONOXIDE ALARM", "co"), ("SMOKE / CO COMBO ALARM", "sc"), ("1-HR FIRE RATED WALL", "fr"),
    ]
    cols = 4
    cw = w / cols
    for i, (label, kind) in enumerate(items):
        cx = x + 0.15 + (i % cols) * cw
        cy = y - 0.15 - (i // cols) * 0.95
        sx, sy = cx + 0.45, cy - 0.25      # symbol center
        L = {"layer": "A-ANNO"}
        if kind == "pl":
            msp.add_line((cx, sy), (cx + 0.9, sy), dxfattribs={"layer": "C-PROP"})
        elif kind == "sb":
            msp.add_line((cx, sy), (cx + 0.9, sy), dxfattribs={"layer": "C-SETB"})
        elif kind == "nw":
            rect(msp, cx, sy - 0.04, cx + 0.9, sy + 0.04, "A-WALL")
        elif kind == "dm":
            rect(msp, cx, sy - 0.04, cx + 0.9, sy + 0.04, "A-HIDN")
        elif kind == "dt":
            msp.add_lwpolyline([(sx - .3, sy - .12), (sx + .3, sy - .12), (sx + .3, sy + .12), (sx - .3, sy + .12)], close=True, dxfattribs=L)
            text(msp, "3068", (sx, sy), h=0.1, align=TextEntityAlignment.MIDDLE_CENTER)
        elif kind == "wt":
            msp.add_lwpolyline([(sx, sy + .18), (sx + .22, sy - .14), (sx - .22, sy - .14)], close=True, dxfattribs=L)
            text(msp, "A", (sx, sy - 0.02), h=0.1, align=TextEntityAlignment.MIDDLE_CENTER)
        elif kind == "kn":
            msp.add_lwpolyline([(sx + .17 * math.cos(math.radians(a)), sy + .17 * math.sin(math.radians(a))) for a in range(0, 360, 60)], close=True, dxfattribs=L)
            text(msp, "1", (sx, sy), h=0.1, align=TextEntityAlignment.MIDDLE_CENTER)
        elif kind == "dc":
            msp.add_circle((sx, sy), 0.22, dxfattribs=L)
            msp.add_line((sx - .22, sy), (sx + .22, sy), dxfattribs=L)
            text(msp, "1", (sx, sy + .1), h=0.09, align=TextEntityAlignment.MIDDLE_CENTER)
            text(msp, "A6.0", (sx, sy - .1), h=0.07, align=TextEntityAlignment.MIDDLE_CENTER)
        elif kind == "em":
            msp.add_circle((sx, sy), 0.18, dxfattribs=L)
            msp.add_solid([(sx - .13, sy + .13), (sx + .13, sy + .13), (sx, sy + .32)], dxfattribs=L)
            text(msp, "1", (sx, sy), h=0.09, align=TextEntityAlignment.MIDDLE_CENTER)
        elif kind == "se":
            msp.add_line((sx - .1, sy - .1), (sx + .1, sy + .1), dxfattribs=L)
            msp.add_line((sx - .1, sy + .1), (sx + .1, sy - .1), dxfattribs=L)
            text(msp, "100.00", (sx + .15, sy + .05), h=0.08)
        elif kind == "df":
            msp.add_line((cx, sy), (cx + 0.8, sy), dxfattribs=L)
            msp.add_solid([(cx + .8, sy + .06), (cx + .8, sy - .06), (cx + .95, sy)], dxfattribs=L)
            text(msp, "2%", (cx + .35, sy + .07), h=0.08)
        elif kind == "na":
            north_arrow(msp, (sx, sy - 0.05), size=0.4)
        elif kind in ("sa", "co", "sc"):
            msp.add_circle((sx, sy), 0.16, dxfattribs=L)
            text(msp, {"sa": "S", "co": "CO", "sc": "S/CO"}[kind], (sx, sy), h=0.07 if kind == "sc" else 0.09,
                 align=TextEntityAlignment.MIDDLE_CENTER)
        elif kind == "fr":
            rect(msp, cx, sy - 0.05, cx + 0.9, sy + 0.05, "A-WALL")
            for k in range(9):
                msp.add_line((cx + k * 0.1, sy - 0.05), (cx + k * 0.1 + 0.1, sy + 0.05), dxfattribs=L)
        text(msp, label, (cx + 1.1, sy - 0.05), h=0.11)
