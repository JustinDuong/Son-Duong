"""A0.0 - Cover sheet & project data."""
import json

from ezdxf.enums import TextEntityAlignment

from plans import adu_model as M
from plans.lib import PROJECT, ROOT, ft_in, mtext, new_sheet, rect, text
from plans.sheet_index import SHEET_INDEX

NUMBER, TITLE = "A0.0", "COVER SHEET & PROJECT DATA"
H = 0.14          # body text height
LS = 0.25         # line spacing


def header(msp, x, y, w, title):
    """Section header bar; returns y of first body line."""
    rect(msp, x, y - 0.32, x + w, y, "A-ANNO")
    text(msp, title, (x + w / 2, y - 0.16), h=0.16, layer="A-ANNO-TITL", align=TextEntityAlignment.MIDDLE_CENTER)
    return y - 0.55


def rows(msp, x, y, items, col2, w=None):
    """Two-column label/value rows; returns next y."""
    for k, v in items:
        text(msp, k, (x + 0.1, y), h=H)
        if w:
            mtext(msp, v, (x + col2, y + H), h=H, width=w)
            y -= LS * max(1, (len(v) * H * 0.9) // w + 1)
        else:
            text(msp, v, (x + col2, y), h=H)
            y -= LS
    return y


def para(msp, x, y, lines, w):
    """Numbered/plain lines as wrapped mtext; returns approx next y."""
    for ln in lines:
        mtext(msp, ln, (x + 0.1, y + H), h=H, width=w - 0.2)
        n = max(1, int(len(ln) * H * 0.82 / (w - 0.2)) + 1)
        y -= LS * n + 0.04
    return y


def vicinity_map(msp, x0, y0, size):
    """Real street centerlines from OC GIS, clipped to a square frame."""
    data = json.loads((ROOT / "research" / "vicinity_streets.json").read_text())
    R = data["radius_ft"]
    k = size / (2 * R)
    cx, cy = x0 + size / 2, y0 + size / 2
    site = (58, 31)  # lot center, ft from SW lot corner
    rect(msp, x0, y0, x0 + size, y0 + size, "A-ANNO")

    def P(p):
        return (cx + (p[0] - site[0]) * k, cy + (p[1] - site[1]) * k)

    def inside(q):
        return x0 < q[0] < x0 + size and y0 < q[1] < y0 + size

    labeled = set()
    for s in data["streets"]:
        pts = [P(p) for p in s["pts"]]
        seg = []
        for q in pts + [None]:
            if q is not None and inside(q):
                seg.append(q)
                continue
            if len(seg) > 1:
                msp.add_lwpolyline(seg, dxfattribs={"layer": "A-ANNO", "lineweight": 50 if s["kind"] == "arterial" else 13})
            seg = []
        if s["kind"] == "arterial" and s["name"] not in labeled:
            vis = [q for q in pts if inside(q)]
            if len(vis) > 2:
                a, b = vis[len(vis) // 2 - 1], vis[len(vis) // 2]
                import math
                ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
                ang = ang + 180 if ang > 90 else (ang - 180 if ang < -90 else ang)
                text(msp, s["name"], (a[0] + 0.12, a[1] + 0.12), h=0.12, rot=ang, layer="A-ANNO-TITL")
                labeled.add(s["name"])
    hn = [s for s in data["streets"] if s["name"] == "HUNTER LN"]
    if hn:
        q = P(hn[0]["pts"][0])
        text(msp, "HUNTER LN", (cx + 0.1, cy - 1.4), h=0.1, rot=90)
    msp.add_circle((cx, cy), 0.14, dxfattribs={"layer": "A-ANNO-TITL"})
    msp.add_circle((cx, cy), 0.05, dxfattribs={"layer": "A-ANNO-TITL"})
    text(msp, "PROJECT SITE", (cx + 0.22, cy + 0.08), h=0.12, layer="A-ANNO-TITL")
    # north arrow
    nx, ny = x0 + size - 0.4, y0 + size - 0.55
    msp.add_lwpolyline([(nx, ny + 0.3), (nx - 0.1, ny - 0.15), (nx, ny - 0.05), (nx + 0.1, ny - 0.15)], close=True,
                       dxfattribs={"layer": "A-ANNO"})
    text(msp, "N", (nx, ny + 0.42), h=0.14, align=TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "NOT TO SCALE", (x0 + 0.1, y0 + 0.12), h=0.08)


def build():
    s = new_sheet(NUMBER, TITLE)
    msp, P = s.msp, PROJECT
    xa, ya, xb, yb = s.drawing_area
    area = round(M.area_sqft())
    porch = round((M.PORCH[1] - M.PORCH[0]) * M.PORCH[2] / 144)

    # ---------------- title band
    text(msp, "NEW DETACHED ACCESSORY DWELLING UNIT (ADU)", (xa + 0.3, yb - 0.75), h=0.48, layer="A-ANNO-TITL")
    text(msp, P["project_address"] + f"   |   APN {P['apn']}", (xa + 0.3, yb - 1.3), h=0.24)
    msp.add_line((xa, yb - 1.6), (xb, yb - 1.6), dxfattribs={"layer": "A-BORDER"})

    top = yb - 1.9
    C1, C2, C3 = xa + 0.2, xa + 10.6, xa + 20.4
    W1, W2, W3 = 10.0, 9.4, 9.6

    # ================= column 1
    y = header(msp, C1, top, W1, "SCOPE OF WORK")
    y = para(msp, C1, y, [
        f"1. CONSTRUCT A NEW 1-STORY DETACHED ADU, {area} SF CONDITIONED: 2 BEDROOMS, 2 BATHROOMS, "
        "KITCHEN, LIVING ROOM, LAUNDRY, WALK-IN CLOSET, COVERED ENTRY PORCH.",
        "2. NEW HEAT PUMP SPLIT SYSTEM (HVAC) FOR ADU.",
        "3. NEW 200A ELECTRICAL SUB-PANEL FOR ADU; SERVICE UPGRADE PER ELECTRICAL PLAN.",
        "4. NEW NEEA-RATED HEAT PUMP WATER HEATER.",
        "5. NEW WATER AND GAS SERVICE TO ADU PER UTILITY / PLUMBING PLAN.",
        "6. PHOTOVOLTAIC SYSTEM PER TITLE 24 (DEFERRED SUBMITTAL).",
        "7. EXISTING 1-STORY SINGLE-FAMILY RESIDENCE TO REMAIN - NO WORK.",
    ], W1)

    y = header(msp, C1, y - 0.15, W1, "PROJECT DATA")
    y = rows(msp, C1, y, [
        ("ADDRESS", P["project_address"]),
        ("APN", P["apn"]),
        ("LEGAL", P["tract"]),
        ("JURISDICTION", "COUNTY OF ORANGE - UNINCORPORATED (OC PUBLIC WORKS)"),
        ("ZONING", "R1 SINGLE-FAMILY RESIDENCE"),
        ("GENERAL PLAN", P["general_plan"]),
        ("ADU REGULATIONS", "OC ZONING CODE SEC. 7-9-90 / GOV. CODE 66314 ET SEQ."),
        ("OCCUPANCY", "R-3"),
        ("CONSTRUCTION TYPE", "V-B"),
        ("FIRE SPRINKLERS", "NOT REQUIRED (ADU >= 5' FROM P/L; MAIN HOUSE NOT SPRINKLERED)"),
        ("STORIES / HEIGHT", "1 STORY / 13'-9\" TO RIDGE (MAX. 16'-0\")"),
        ("FLOOD ZONE", "FEMA ZONE X (0.2% ANNUAL CHANCE) - NOT SFHA"),
        ("SEISMIC HAZARD", "STATE LIQUEFACTION ZONE - SOILS REPORT REQUIRED"),
        ("FIRE HAZARD ZONE", "NONE (NOT VHFHSZ)"),
        ("SEWER / WATER", "MIDWAY CITY SANITARY DIST. / VERIFY WATER PURVEYOR"),
    ], 2.8)

    y = header(msp, C1, y - 0.15, W1, "SETBACKS (ADU)")
    y = rows(msp, C1, y, [
        ("", "REQUIRED (7-9-90) / PROVIDED"),
        ("REAR (WEST)", "4'-0\" MIN. / 5'-0\""),
        ("SIDE (SOUTH)", "4'-0\" MIN. / 5'-0\""),
        ("SIDE (NORTH)", "4'-0\" MIN. / " + ft_in(M.LOT_W_NS - M.ADU_ORIGIN_ON_LOT[1] - M.L - M.PORCH[2]) + " (TO PORCH)"),
        ("TO (E) STRUCTURES", "SEE SITE PLAN A1.0"),
    ], 2.8)

    # ================= column 2
    lot = 7215
    house, patio = 1669, 274
    cov = house + patio + area + porch
    y = header(msp, C2, top, W2, "AREA SUMMARY & LOT COVERAGE")
    y = rows(msp, C2, y, [
        ("LOT AREA (GIS - VERIFY BY SURVEY)", f"{lot:,} SF  (62.2' x 116.0')"),
        ("(E) RESIDENCE LIVING AREA", "1,011 SF"),
        ("(E) RES. + GARAGE FOOTPRINT (GIS)", f"{house:,} SF"),
        ("(E) PATIO COVER (APPROX.)", f"{patio:,} SF"),
        ("(E) SHED", "TBD - TO REMAIN OR BE REMOVED"),
        ("(N) ADU CONDITIONED AREA", f"{area:,} SF   (<= 800 SF ALLOWED)"),
        ("(N) COVERED ENTRY PORCH", f"{porch:,} SF"),
        ("TOTAL BUILDING COVERAGE", f"{cov:,} SF = {100 * cov / lot:.1f}%   (R1: NO MAXIMUM)"),
    ], 5.2)

    y = header(msp, C2, y - 0.15, W2, "PARKING")
    y = para(msp, C2, y, [
        "(E) RESIDENCE: 2 SPACES (EXISTING, TO REMAIN).",
        "(N) ADU: 0 SPACES - EXEMPT PER OC ZONING 7-9-90(d)(4)(a): ADU IS WITHIN 1/2 MILE WALKING "
        "DISTANCE OF PUBLIC TRANSIT (OCTA BUS STOP - VERIFY ID/DISTANCE ON VICINITY MAP). "
        "IF NOT EXEMPT, 1 TANDEM SPACE ON (E) DRIVEWAY.",
    ], W2)

    y = header(msp, C2, y - 0.15, W2, "APPLICABLE CODES")
    y = para(msp, C2, y, [
        "ALL WORK SHALL COMPLY WITH THE 2025 CALIFORNIA BUILDING STANDARDS CODE (TITLE 24) AS ADOPTED "
        "AND AMENDED BY THE COUNTY OF ORANGE:",
        "2025 CA RESIDENTIAL CODE (CRC) / 2025 CA BUILDING CODE (CBC)",
        "2025 CA ELECTRICAL CODE (CEC) / 2025 CA MECHANICAL CODE (CMC)",
        "2025 CA PLUMBING CODE (CPC) / 2025 CA FIRE CODE (CFC)",
        "2025 CA ENERGY CODE / 2025 CALGREEN (CGBSC)",
        "COUNTY OF ORANGE ZONING CODE & CODIFIED ORDINANCES.",
    ], W2)

    y = header(msp, C2, y - 0.15, W2, "DEFERRED SUBMITTALS")
    y = para(msp, C2, y, [
        "1. PHOTOVOLTAIC (PV) SYSTEM - SEPARATE PERMIT; MUST BE APPROVED PRIOR TO ROOF SHEATHING INSPECTION.",
        "2. PRE-FABRICATED ROOF TRUSSES (IF USED) - CALCS REVIEWED BY ENGINEER OF RECORD.",
    ], W2)

    y = header(msp, C2, y - 0.15, W2, "ADU NOTES")
    y = para(msp, C2, y, [
        "1. ADU SHALL NOT BE SOLD SEPARATELY FROM THE PRIMARY DWELLING.",
        "2. ADU MAY BE RENTED FOR TERMS LONGER THAN 30 DAYS ONLY; NO SHORT-TERM RENTAL.",
        "3. ADU HAS DIRECT EXTERIOR ACCESS INDEPENDENT OF THE PRIMARY DWELLING.",
        "4. NEW ADDRESS FOR ADU TO BE REQUESTED VIA MYOCESERVICES AFTER BUILDING PERMIT SUBMITTAL.",
        "5. ALL NEW UTILITY SERVICE LINES SHALL BE INSTALLED UNDERGROUND.",
    ], W2)

    # ================= column 3
    y = header(msp, C3, top, W3, "SHEET INDEX")
    for num, title in SHEET_INDEX:
        text(msp, num, (C3 + 0.15, y), h=H)
        text(msp, title, (C3 + 1.0, y), h=H)
        y -= LS
    y -= 0.1

    y = header(msp, C3, y, W3, "PROJECT DIRECTORY")
    y = rows(msp, C3, y, [
        ("PREPARED BY", P["designer"]),
        ("STRUCTURAL ENGINEER", "TBD"),
        ("SOILS ENGINEER", "TBD (REPORT REQUIRED - LIQUEFACTION ZONE)"),
        ("TITLE 24 CONSULTANT", "TBD"),
        ("BUILDING DEPT.", "OC PUBLIC WORKS - DEVELOPMENT SERVICES"),
        ("", "601 N. ROSS ST, SANTA ANA, CA 92701  (714) 667-8888"),
    ], 2.8)

    y = header(msp, C3, y - 0.15, W3, "VICINITY MAP")
    size = min(W3 - 0.4, y - ya - 0.3)
    vicinity_map(msp, C3 + (W3 - size) / 2, y - size, size)

    # ---------------- footer
    mtext(msp, "THESE DRAWINGS ARE NOT VALID FOR PERMIT OR CONSTRUCTION UNTIL REVIEWED, SIGNED AND STAMPED BY "
               "A LICENSED PROFESSIONAL WHERE REQUIRED BY THE JURISDICTION. CONTRACTOR SHALL VERIFY ALL "
               "DIMENSIONS AND CONDITIONS AT THE SITE.", (C1, ya + 0.55), h=0.1, width=19)
    return s
