"""A1.0 - Site plan.

Lot coordinates (feet): SW lot corner = (0, 0), +X east toward Hunter Ln, +Y north.
Lot geometry, house footprint and elevations from OC GIS (see research/). A licensed survey governs.
Utility locations of existing meters/panel/sewer are not shown on the reference plan -> marked VIF.
"""
import json
import math

from ezdxf.enums import TextEntityAlignment

from plans import adu_model as M
from plans.adu_draw import btext
from plans.lib import PROJECT, ROOT, SCALES, dim, new_drawing_block, new_sheet, north_arrow, place_drawing, text
from plans.textblocks import header, para, rows

NUMBER, TITLE = "A1.0", "SITE PLAN"
SC = '3/16" = 1\'-0"'
SCALES.setdefault(SC, 1 / 64)

F = 12.0  # feet -> inches


def P(x, y):
    """Lot feet -> block inches."""
    return (x * F, y * F)


# ---------------------------------------------------------------- site layout (feet)
LOT_X, LOT_Y = 116.0, 62.2
CL_X = 140.5                                  # Hunter Ln centerline
AX, AY = M.ADU_ORIGIN_ON_LOT[0] / F, M.ADU_ORIGIN_ON_LOT[1] / F
AW, AL = M.W / F, M.L / F
PORCH = (AX + M.PORCH[0] / F, AY + AL, AX + M.PORCH[1] / F, AY + AL + M.PORCH[2] / F)
PATIO = (42.0, 23.0, 56.4, 42.0)              # approx. from aerial
SHED = (36.0, 13.0, 48.0, 23.0)               # approx. from aerial - to be removed
DRIVE = (81.6, 41.6, 116.0, 62.2)             # (E) driveway (aerial)

# utilities (assumed, VIF)
WTR_E = (113.0, 57.5)        # (E) water meter in parkway/front yard
WTR_N = (113.0, 54.5)        # (N) water meter
GAS_E = (64.0, 59.6)         # (E) gas meter on north wall of house
GAS_N = (61.0, 59.6)         # (N) gas meter
ELE_E = (70.0, 59.6)         # (E) electric meter / 200A panel
SUB_ADU = (AX + 4.6, AY + AL + 0.5)  # (N) 200A sub-panel on ADU north wall (exterior)
TRENCH_Y = 61.0
ADU_STUB = (AX + 3.0, AY + AL)       # utilities enter ADU at NW (kitchen/laundry side)
SEWER_OUT = (AX + 2.5, AY + AL)      # sewer leaves north wall near laundry/baths
SEWER_TIE = (57.0, 61.6)             # connect to (E) building sewer (VIF)
CONDENSER = (AX + AW + 1.0, AY + 9.0, AX + AW + 4.0, AY + 12.0)    # east side, between bedroom windows
WH = (AX + 0.3, AY + AL + 0.2, AX + 2.8, AY + AL + 2.7)            # HPWH enclosure at NW corner

ELEV = json.loads((ROOT / "research" / "elevations_dem.json").read_text())["points"]
FF = 47.60


def poly_len(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


WATER_RUN = [WTR_N, (WTR_N[0], TRENCH_Y), (ADU_STUB[0], TRENCH_Y), ADU_STUB]
GAS_RUN = [GAS_N, (GAS_N[0], TRENCH_Y), (ADU_STUB[0], TRENCH_Y), ADU_STUB]
ELEC_RUN = [ELE_E, (ELE_E[0], TRENCH_Y), (SUB_ADU[0], TRENCH_Y), SUB_ADU]
SEWER_RUN = [SEWER_OUT, (SEWER_OUT[0], SEWER_TIE[1]), SEWER_TIE]

KEYNOTES = [
    "(E) 1-STORY SINGLE-FAMILY RESIDENCE TO REMAIN. NO WORK.",
    "(E) PATIO COVER TO REMAIN.",
    "(E) SHED TO BE REMOVED.",
    "(E) DRIVEWAY - 2 PARKING SPACES FOR (E) RESIDENCE TO REMAIN.",
    "(E) 6' HIGH BLOCK WALL AT SIDE AND REAR PROPERTY LINES TO REMAIN (V.I.F.).",
    "(E) WATER METER (V.I.F.).",
    "(N) WATER METER FOR ADU PER WATER PURVEYOR; (N) 1\" WATER LINE TO ADU.",
    "(E) GAS METER (V.I.F.).",
    "(N) GAS METER W/ (N) 1-1/4\" GAS LINE TO ADU. SEE P1.0.",
    "(E) ELECTRIC METER/200A PANEL: REPLACE W/ (N) 400A DUAL-GANG METER MAIN; (E) PANEL BECOMES SUB-PANEL. SEE E1.0.",
    "(N) 200A SUB-PANEL AT ADU, UNDERGROUND FEEDER IN CONDUIT. SEE E1.0.",
    "(N) COMMON UTILITY TRENCH (WATER / GAS / ELECTRIC) - UNDERGROUND. MAINTAIN CPC SEPARATIONS.",
    "(N) 4\" SEWER @ 2% MIN. TO (E) BUILDING SEWER W/ WYE AND 2-WAY CLEANOUT (V.I.F.). SEE P1.0.",
    "(N) HEAT PUMP CONDENSER ON 3\" CONC. PAD. SEE M1.0.",
    "(N) HEAT PUMP WATER HEATER IN EXTERIOR ENCLOSURE ON 3\" CONC. PAD. SEE P1.0.",
    "(N) 3'-0\" WIDE PERVIOUS PATH (PAVERS ON SAND) FROM (E) DRIVEWAY TO ADU ENTRY.",
    "1-HR FIRE-RESISTIVE EAVE / PROJECTION WHERE F.S.D. < 5'-0\". SEE A6.0.",
    "(E) TREES / SHRUBS WITHIN ADU AREA TO BE REMOVED.",
    "(N) GUTTER & DOWNSPOUT W/ SPLASH BLOCK; DRAIN TO LANDSCAPE, AWAY FROM FOUNDATION.",
]


def kn(blk, n, at, to=None):
    """Hexagon keynote tag at `at` (lot ft) with optional leader to `to`."""
    r = 1.15
    cx, cy = at
    pts = [P(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    blk.add_lwpolyline(pts, close=True, dxfattribs={"layer": "A-ANNO"})
    btext(blk, str(n), P(cx, cy), 0.09, SC)
    if to:
        ang = math.atan2(to[1] - cy, to[0] - cx)
        blk.add_line(P(cx + r * math.cos(ang), cy + r * math.sin(ang)), P(*to), dxfattribs={"layer": "A-ANNO"})
        blk.add_circle(P(*to), 2.0, dxfattribs={"layer": "A-ANNO"})


def rect_ft(blk, r, layer):
    x0, y0, x1, y1 = r
    blk.add_lwpolyline([P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)], close=True, dxfattribs={"layer": layer})


def run(blk, pts, layer, label=None, label_at=None):
    blk.add_lwpolyline([P(*p) for p in pts], dxfattribs={"layer": layer})
    if label:
        btext(blk, label, P(*label_at), 0.08, SC, align=TextEntityAlignment.MIDDLE_LEFT)


def spot(blk, xy, val, prefix=""):
    x, y = xy
    blk.add_line(P(x - .5, y - .5), P(x + .5, y + .5), dxfattribs={"layer": "A-ANNO"})
    blk.add_line(P(x - .5, y + .5), P(x + .5, y - .5), dxfattribs={"layer": "A-ANNO"})
    btext(blk, f"{prefix}{val:.2f}", P(x + .8, y + .5), 0.08, SC, align=TextEntityAlignment.MIDDLE_LEFT)


def arrow(blk, a, b, label="2%"):
    blk.add_line(P(*a), P(*b), dxfattribs={"layer": "A-ANNO"})
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    h = 1.0
    l = (b[0] - h * math.cos(ang - .35), b[1] - h * math.sin(ang - .35))
    r = (b[0] - h * math.cos(ang + .35), b[1] - h * math.sin(ang + .35))
    blk.add_solid([P(*b), P(*l), P(*r)], dxfattribs={"layer": "A-ANNO"})
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    btext(blk, label, P(m[0], m[1] + .7), 0.08, SC, rot=math.degrees(ang) if abs(math.degrees(ang)) <= 90 else math.degrees(ang) + 180)


def draw(blk):
    # ---- property lines + street
    blk.add_lwpolyline([P(0, 0), P(LOT_X, 0), P(LOT_X, LOT_Y), P(0, LOT_Y)], close=True, dxfattribs={"layer": "C-PROP"})
    blk.add_line(P(CL_X, -6), P(CL_X, LOT_Y + 2.5), dxfattribs={"layer": "A-GRID"})
    blk.add_line(P(LOT_X + 6.5, -6), P(LOT_X + 6.5, LOT_Y + 2.5), dxfattribs={"layer": "A-HIDN"})  # curb (approx.)
    btext(blk, "HUNTER LN", P(CL_X - 3, LOT_Y / 2), 0.16, SC, rot=90)
    btext(blk, "(PUBLIC STREET)", P(CL_X - 6, LOT_Y / 2), 0.09, SC, rot=90)
    btext(blk, "C/L", P(CL_X + 1.5, LOT_Y + 1.5), 0.08, SC)
    btext(blk, "(E) CURB (APPROX.)", P(LOT_X + 7.8, 10), 0.08, SC, rot=90)
    for lab, xy, rot in [("P/L  116.00'", (LOT_X / 2, -1.6), 0), ("P/L  116.00'", (LOT_X / 2, LOT_Y + 1.6), 0),
                         ("P/L  62.20'", (-1.6, LOT_Y / 2), 90), ("P/L  62.20'", (LOT_X + 1.6, LOT_Y / 2), 90)]:
        btext(blk, lab, P(*xy), 0.08, SC, rot=rot)
    # setback lines: ADU 4' side/rear; R1 front 20'
    blk.add_lwpolyline([P(4, 4), P(LOT_X - 20, 4), P(LOT_X - 20, LOT_Y - 4), P(4, LOT_Y - 4)], close=True,
                       dxfattribs={"layer": "C-SETB"})
    btext(blk, "4'-0\" ADU SIDE/REAR SETBACK", P(30, 3.0), 0.08, SC)
    btext(blk, "20'-0\" FRONT SETBACK", P(LOT_X - 21.2, 30), 0.08, SC, rot=90)

    # ---- existing
    fp = json.loads((ROOT / "research" / "site_gis.json").read_text())["existing_footprint_gis_ft"]
    hp = [P(x, y) for x, y in fp]
    blk.add_lwpolyline(hp, close=True, dxfattribs={"layer": "A-WALL"})
    btext(blk, "(E) 1-STORY RESIDENCE", P(73, 33), 0.11, SC)
    btext(blk, "1,011 SF LIVING  /  NO WORK", P(73, 30.5), 0.09, SC)
    btext(blk, "(E) GARAGE (V.I.F.)", P(69, 50), 0.09, SC)
    rect_ft(blk, PATIO, "A-WALL")
    btext(blk, "(E) PATIO COVER", P(49.2, 33.5), 0.09, SC, rot=90)
    rect_ft(blk, SHED, "A-HIDN")
    btext(blk, "(E) SHED", P(42, 18.6), 0.08, SC)
    btext(blk, "TO BE REMOVED", P(42, 17.0), 0.08, SC)
    rect_ft(blk, DRIVE, "A-HIDN")
    btext(blk, "(E) DRIVEWAY", P(99, 52), 0.08, SC)
    btext(blk, "2 PARKING SPACES", P(99, 49.8), 0.08, SC)

    # ---- (N) ADU with hatch-like double outline
    ax0, ay0, ax1, ay1 = AX, AY, AX + AW, AY + AL
    rect_ft(blk, (ax0, ay0, ax1, ay1), "A-WALL")
    rect_ft(blk, (ax0 + .35, ay0 + .35, ax1 - .35, ay1 - .35), "A-WALL")
    for k in range(1, 26):  # diagonal hatch
        y = ay0 + k * 1.6
        blk.add_line(P(ax0 + .35, min(y, ay1 - .35)), P(min(ax1 - .35, ax0 + .35 + (ay1 - .35 - y)), min(ay1 - .35, y + (ax1 - ax0))),
                     dxfattribs={"layer": "A-WALL-HTCH"}) if y < ay1 - .35 else None
    rect_ft(blk, PORCH, "A-WALL")
    btext(blk, "(N) DETACHED ADU", P(AX + AW / 2, AY + AL / 2 + 2.2), 0.12, SC)
    btext(blk, f"{M.area_sqft():.0f} SF  /  1 STORY  /  13'-9\" MAX. HT.", P(AX + AW / 2, AY + AL / 2 - .2), 0.09, SC)
    btext(blk, f"F.F. = {FF:.2f}", P(AX + AW / 2, AY + AL / 2 - 2.2), 0.09, SC)
    btext(blk, "PORCH", P((PORCH[0] + PORCH[2]) / 2, (PORCH[1] + PORCH[3]) / 2), 0.08, SC)
    # eave line (1'-0" overhang assumed)
    e = 1.0
    blk.add_lwpolyline([P(ax0 - e, ay0 - e), P(ax1 + e, ay0 - e), P(ax1 + e, ay1 + e), P(ax0 - e, ay1 + e)], close=True,
                       dxfattribs={"layer": "A-HIDN"})

    # ---- equipment
    rect_ft(blk, CONDENSER, "A-ANNO")
    btext(blk, "HP", P((CONDENSER[0] + CONDENSER[2]) / 2, (CONDENSER[1] + CONDENSER[3]) / 2), 0.08, SC)
    wh = WH
    rect_ft(blk, wh, "A-ANNO")
    btext(blk, "WH", P((wh[0] + wh[2]) / 2, (wh[1] + wh[3]) / 2), 0.08, SC)

    # ---- path (pervious)
    path = [(PORCH[0] + 1, PORCH[3]), (PORCH[0] + 1, TRENCH_Y - 1.0), (DRIVE[0], TRENCH_Y - 1.0)]
    blk.add_lwpolyline([P(*p) for p in path], dxfattribs={"layer": "A-HIDN"})

    # ---- utilities
    run(blk, WATER_RUN, "P-FIXT")
    run(blk, GAS_RUN, "P-FIXT")
    run(blk, ELEC_RUN, "E-POWR")
    run(blk, SEWER_RUN, "P-FIXT")
    for xy, lab in [(WTR_E, "WM"), (WTR_N, "WM"), (GAS_E, "GM"), (GAS_N, "GM"), (ELE_E, "EM"), (SUB_ADU, "SP")]:
        rect_ft(blk, (xy[0] - .7, xy[1] - .5, xy[0] + .7, xy[1] + .5), "A-ANNO")
        btext(blk, lab, P(*xy), 0.08, SC)
    blk.add_circle(P(*SEWER_TIE), 6, dxfattribs={"layer": "P-FIXT"})
    btext(blk, "W / G / E TRENCH", P(36, TRENCH_Y + 0.7), 0.08, SC)
    btext(blk, "4\" SEWER", P(57.5, TRENCH_Y + 1.6), 0.08, SC, align=TextEntityAlignment.MIDDLE_LEFT)

    # ---- elevations & drainage
    for name in ("SW lot corner", "NW lot corner", "SE lot corner", "NE lot corner", "rear yard mid", "front P/L mid"):
        x, y = ELEV[name]["xy_ft"]
        x = min(max(x, 1.2), LOT_X - 1.2)
        y = min(max(y, 1.2), LOT_Y - 1.2)
        spot(blk, (x, y), ELEV[name]["value"], "EG ")
    for name in ("ADU SW", "ADU NW", "ADU SE", "ADU NE"):
        x, y = ELEV[name]["xy_ft"]
        spot(blk, (x + (-1.6 if x < 10 else 1.6), y + (-1.6 if y < 10 else 1.6)), ELEV[name]["value"], "EG ")
    for a, b in [((AX + AW + 1.5, AY + 22), (AX + AW + 9, AY + 22)), ((AX + 8, AY - .6), (AX + 8, 1.2)),
                 ((AX + AW - 2, AY + AL + 1.5), (AX + AW - 2, AY + AL + 6.5)), ((AX - .6, AY + 22), (1.0, AY + 22)),
                 ((60, 10), (90, 8)), ((88, 30), (110, 30)), ((60, 52), (78, 52))]:
        arrow(blk, a, b)
    btext(blk, "SURFACE DRAINAGE TO STREET (E)", P(100, 26.5), 0.08, SC)

    # ---- dimensions (real inches)
    d = lambda a, b, off: dim(blk, P(*a), P(*b), off * F, SC)
    d((0, 0), (LOT_X, 0), -7)
    d((0, 0), (0, LOT_Y), 7)
    d((0, AY + 9), (AX, AY + 9), 0)
    d((AX + 15, 0), (AX + 15, AY), 0)
    d((AX + 15, AY + AL), (AX + 15, LOT_Y), 0)
    d((AX, AY - 1), (AX + AW, AY - 1), -2.5)
    d((AX + AW, AY), (AX + AW, AY + AL), -5.5)
    d((AX + AW, AY + 26), (PATIO[0], AY + 26), 0)
    d((91.3, 20), (LOT_X, 20), 0)   # (E) front yard (house to front P/L)
    d((LOT_X, 12), (CL_X, 12), 0)

    # ---- keynote tags (number, tag position, leader target)
    tags = [
        (1, (66, 22), (70, 26)), (2, (49, 46.5), (49, 41)), (3, (42, 10.5), (42, 13.5)), (4, (106, 44), (100, 47)),
        (5, (-3.5, 20), (0, 18)), (6, (119.5, 57.5), WTR_E), (7, (119.5, 53.5), WTR_N), (8, (66, 65.5), GAS_E),
        (9, (59, 65.5), GAS_N), (10, (73, 65.5), ELE_E), (11, (AX + 8.5, AY + AL + 6.5), SUB_ADU),
        (12, (40, 65.5), (40, TRENCH_Y)), (13, (52, 65.5), (52, SEWER_TIE[1])), (14, (AX + AW + 6.5, AY + 10.5), (CONDENSER[2], AY + 10.5)),
        (15, (AX - 2.6, AY + AL + 4.5), (wh[0], (wh[1] + wh[3]) / 2)), (16, (32, 55.5), (32, TRENCH_Y - 1)),
        (17, (AX - 2.6, AY + 12), (AX - 1, AY + 10)), (18, (31.5, 16), (AX + AW - 1, AY + 9)),
        (19, (AX + AW + 4.5, AY + 4), (AX + AW, AY + 1.0)),
    ]
    for n, at, to in tags:
        kn(blk, n, at, to)


def build():
    s = new_sheet(NUMBER, TITLE)
    msp = s.msp
    xa, ya, xb, yb = s.drawing_area
    blk = new_drawing_block(s, "SITE_PLAN")
    draw(blk)
    k = SCALES[SC]
    ox, oy = xa + 1.6, ya + 9.9          # lot SW corner on paper
    place_drawing(s, "SITE_PLAN", (ox, oy), SC, "SITE PLAN", title_pos=(xa + 0.4, ya + 7.75), detail_no="1")
    north_arrow(msp, (ox + (CL_X - 3) * F * k, oy - 0.9), size=0.8)

    # ---------- bottom band: data + keynotes + legend
    top = ya + 7.2
    c1, w1 = xa + 0.2, 7.0
    y = header(msp, c1, top, w1, "SITE DATA")
    lot = 7215
    imp_new = round(M.area_sqft()) + 22 + 9 + 6
    y = rows(msp, c1, y, [
        ("ADDRESS / APN", f"14721 HUNTER LN / {PROJECT['apn']}"),
        ("ZONING / GEN. PLAN", "R1 / 1B SUBURBAN RES."),
        ("GROSS LOT AREA", f"{lot:,} SF (0.166 AC)"),
        ("NET LOT AREA", f"{lot:,} SF (0.166 AC) - NO R/W DEDICATION"),
        ("LOT COVERAGE", "2,744 SF = 38.0% (SEE A0.0)"),
        ("AVG. LOT SLOPE", "1.5% (46.68 REAR TO 44.84 FRONT)"),
        ("(N) IMPERVIOUS AREA", f"{imp_new:,} SF (ADU, PORCH, EQUIP. PADS)"),
        ("REPLACED IMPERVIOUS", "0 SF"),
        ("EASEMENTS", "NONE KNOWN - VERIFY W/ TITLE REPORT"),
        ("GRADING", "NONE; FINE GRADING ONLY (< 50 CY)"),
    ], 2.7)

    c2, w2 = xa + 7.5, 14.6
    y2 = header(msp, c2, top, w2, "SITE PLAN KEYNOTES")
    half = (len(KEYNOTES) + 1) // 2
    for i, note in enumerate(KEYNOTES):
        cx = c2 + (w2 / 2 if i >= half else 0)
        cy = y2 - (i % half) * 0.6
        text(msp, str(i + 1), (cx + 0.2, cy - 0.05), h=0.11, align=TextEntityAlignment.MIDDLE_CENTER)
        msp.add_lwpolyline([(cx + 0.2 + 0.17 * math.cos(math.radians(a)), cy - 0.05 + 0.17 * math.sin(math.radians(a)))
                            for a in range(0, 360, 60)], close=True, dxfattribs={"layer": "A-ANNO"})
        para(msp, cx + 0.35, cy + 0.02, [note], w2 / 2 - 0.4)

    c3, w3 = xa + 22.4, xb - xa - 22.6
    y3 = header(msp, c3, top, w3, "UTILITY RUNS (APPROX.)")
    y3 = rows(msp, c3, y3, [
        ("WATER  (N) METER TO ADU", f"{poly_len(WATER_RUN):.0f} LF, 1\""),
        ("GAS  (N) METER TO ADU", f"{poly_len(GAS_RUN):.0f} LF, 1-1/4\""),
        ("ELEC.  MAIN TO ADU PANEL", f"{poly_len(ELEC_RUN):.0f} LF"),
        ("SEWER  ADU TO (E) SEWER", f"{poly_len(SEWER_RUN):.0f} LF, 4\" @ 2% MIN."),
        ("WASTEWATER", "PUBLIC SEWER (MIDWAY CITY S.D.)"),
        ("SOLAR PV", "PER TITLE 24 - DEFERRED SUBMITTAL"),
    ], 3.3)
    y3 = header(msp, c3, y3 - 0.1, w3, "NOTES")
    para(msp, c3, y3, [
        "1. LOT LINES, HOUSE FOOTPRINT AND SPOT ELEVATIONS (EG) ARE FROM OC GIS / 2023 OC DEM AND ARE APPROXIMATE. "
        "A BOUNDARY & TOPOGRAPHIC SURVEY BY A LICENSED SURVEYOR GOVERNS.",
        "2. LOCATIONS OF (E) METERS, PANEL AND BUILDING SEWER TO BE VERIFIED IN FIELD.",
        "3. SEE A0.1 FOR SITE, STORM WATER AND CALGREEN NOTES.",
    ], w3)
    return s
