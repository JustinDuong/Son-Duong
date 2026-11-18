"""A2.0 - ADU floor plan, door & window schedules, wall legend, floor plan notes."""
import math

from ezdxf.enums import TextEntityAlignment

from plans import adu_model as M
from plans.adu_draw import btext, draw_adu, opening_pts
from plans.lib import SCALES, dim, ft, ft_in, new_drawing_block, new_sheet, north_arrow, place_drawing, rect, text
from plans.textblocks import header, para

NUMBER, TITLE = "A2.0", "FLOOR PLAN"
SC = '3/8" = 1\'-0"'
E, I = M.EXT_T, M.INT_T

# window marks follow M.WINDOWS order; the 9068 slider is scheduled as a door
WIN_MARKS = ["A", "B", None, "C", "D", "E", "F"]
WINDOWS = {
    "A": ("LIVING", "5'-0\" x 4'-0\"", "XO SLIDER", "3'-0\"", "DUAL GLAZED LOW-E"),
    "B": ("KITCHEN", "5'-0\" x 4'-0\"", "XO SLIDER", "3'-6\"", "OVER SINK"),
    "C": ("BEDROOM 1", "5'-0\" x 4'-0\"", "XO SLIDER", "2'-6\"", "EGRESS - 5.7 SF NET MIN."),
    "D": ("BEDROOM 2", "5'-0\" x 4'-0\"", "XO SLIDER", "2'-6\"", "EGRESS - 5.7 SF NET MIN."),
    "E": ("BATH 1", "2'-0\" x 1'-0\"", "FIXED", "6'-0\"", "TEMPERED, OBSCURE"),
    "F": ("BATH 2", "2'-0\" x 1'-0\"", "FIXED", "6'-0\"", "TEMPERED, OBSCURE"),
}
DOORS = [
    # no, location, size, type, notes
    ("1", "ENTRY", "3'-0\" x 6'-8\"", "EXT. SOLID CORE", "WEATHERSTRIP, DEADBOLT, THRESHOLD 1/2\" MAX."),
    ("2", "LIVING", "9'-0\" x 6'-8\"", "EXT. SLIDING GLASS", "TEMPERED, DUAL GLAZED LOW-E"),
    ("3", "BATH 1", "2'-6\" x 6'-8\"", "INT. HOLLOW CORE", "PRIVACY LOCK"),
    ("4", "BEDROOM 1", "2'-8\" x 6'-8\"", "INT. HOLLOW CORE", "PRIVACY LOCK"),
    ("5", "BEDROOM 2", "2'-6\" x 6'-8\"", "INT. HOLLOW CORE", "PRIVACY LOCK"),
    ("6", "BATH 2", "2'-6\" x 6'-8\"", "INT. HOLLOW CORE", "PRIVACY LOCK"),
    ("7", "W.I.C.", "2'-6\" x 6'-8\"", "INT. BARN (SLIDING)", "SURFACE TRACK"),
]
# door tag positions (ADU coords) for each door number
DOOR_TAGS = {
    "1": (M.ENTRY_DOOR[1] + ft(1, 6), M.L - ft(3, 9)),
    "2": (M.W - ft(2, 3), ft(31, 1)),
    "3": (ft(6, 5), ft(14, 0)),
    "4": (ft(10, 0), ft(11, 8)),
    "5": (ft(7, 3), ft(8, 6)),
    "6": (ft(7, 3), ft(5, 9)),
    "7": (ft(7, 3), ft(2, 3)),
}

KEYNOTES = [
    "SMOKE ALARM (S) / SMOKE + CO COMBO ALARM (S/CO): HARDWIRED, INTERCONNECTED, BATTERY BACKUP (CRC R314, R315).",
    "BATH EXHAUST FAN (EF): ENERGY STAR, 50 CFM MIN., DUCTED TO EXTERIOR, HUMIDISTAT CONTROL (CALGREEN 4.506.1).",
    "ATTIC ACCESS 22\" x 30\" MIN. W/ 30\" CLEAR HEADROOM ABOVE (CRC R807).",
    "RANGE HOOD VENTED TO EXTERIOR, 100 CFM MIN. (CMC 504 / ASHRAE 62.2).",
    "STACKED WASHER / DRYER; DRYER VENT TO EXTERIOR, 14 FT MAX. W/ 2 ELBOWS (CMC 504.4); 4\" MIN. DUCT.",
    "SHOWER: 30\" x 30\" MIN. / 1024 SQ IN; TEMPERED GLASS ENCLOSURE; WALLS NON-ABSORBENT TO 72\" A.F.F.",
    "WATER CLOSET: 15\" MIN. FROM C/L TO SIDE WALL/OBSTRUCTION; 24\" MIN. CLEAR IN FRONT (CPC 402.5).",
    "(N) 200A SUB-PANEL ON EXTERIOR WALL. 30\" W x 36\" D CLEAR WORKING SPACE (CEC 110.26). SEE E1.0.",
    "(N) HEAT PUMP WATER HEATER IN WEATHER-PROOF ENCLOSURE ON 3\" CONC. PAD; SEISMIC STRAPS. SEE P1.0.",
    "(N) HEAT PUMP CONDENSER ON 3\" CONC. PAD. SEE M1.0.",
    "(N) COVERED ENTRY PORCH, CONC. SLAB; LANDING 36\" DEEP MIN., 7-3/4\" MAX. STEP AT DOOR (CRC R311.3).",
    "KITCHEN: SINK, DISHWASHER, RANGE, REFRIGERATOR. COUNTERTOP 25\" DEEP.",
]
# keynote tags (n, tag pos, leader target) in ADU coords
KN_TAGS = [
    (1, (ft(13, 6), ft(18, 0)), None),
    (1, (ft(13, 0), ft(4, 0)), None),
    (1, (ft(7, 2), ft(15, 9)), None),
    (1, (ft(12, 6), ft(30, 3)), None),
    (2, (ft(4, 6), ft(19, 9)), None),
    (2, (ft(4, 6), ft(9, 7)), None),
    (3, (ft(7, 2), ft(20, 3)), None),
    (4, (ft(5, 6), ft(35, 6)), (ft(5, 0), M.L - ft(1, 0))),
    (5, (ft(4, 3), ft(22, 7)), (ft(1, 9), ft(22, 7))),
    (8, (ft(4, 0), M.L + ft(4, 6)), (ft(4, 6), M.L + ft(0, 6))),
    (9, (-ft(3, 0), M.L + ft(3, 0)), (ft(0, 4), M.L + ft(1, 6))),
    (10, (M.W + ft(5, 9), ft(10, 6)), (M.W + ft(3, 0), ft(10, 6))),
    (11, (ft(16, 6), M.L + ft(3, 6)), (ft(14, 2), M.L + ft(2, 0))),
    (12, (ft(9, 0), ft(33, 0)), (ft(2, 6), ft(32, 0))),
]


def clear(x0, y0, x1, y1):
    """Clear room size (ft-in) from wall-line bounds: exterior edges lose E, interior edges lose I/2."""
    def adj(v, lo):
        if v in (0, M.W, M.L):
            return E
        return I / 2
    w = (x1 - x0) - adj(x0, True) - adj(x1, False)
    h = (y1 - y0) - adj(y0, True) - adj(y1, False)
    return w, h


def hexa(blk, c, r, n):
    blk.add_lwpolyline([(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
                        for a in range(0, 360, 60)], close=True, dxfattribs={"layer": "A-ANNO"})
    btext(blk, str(n), c, 0.09, SC)


def draw(blk):
    draw_adu(blk, SC, detail=True, tags=False, labels=False, dims=False)
    k = SCALES[SC]
    W, L = M.W, M.L

    # ---- window tags (triangles)
    for (side, a, b, _), mark in zip(M.WINDOWS, WIN_MARKS):
        if not mark:
            continue
        p1, p2 = opening_pts(side, a, b)
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        off = {"N": (0, ft(2, 3)), "S": (0, -ft(2, 3)), "E": (ft(2, 3), 0), "W": (-ft(2, 3), 0)}[side]
        cx, cy = mx + off[0], my + off[1]
        r = 0.16 / k
        blk.add_lwpolyline([(cx, cy + r), (cx + r * .95, cy - r * .6), (cx - r * .95, cy - r * .6)], close=True,
                           dxfattribs={"layer": "A-ANNO"})
        btext(blk, mark, (cx, cy - r * .1), 0.1, SC)
    # ---- door tags (boxes)
    for n, (x, y) in DOOR_TAGS.items():
        w2, h2 = 0.14 / k, 0.1 / k
        rect(blk, x - w2, y - h2, x + w2, y + h2, "A-ANNO")
        btext(blk, n, (x, y), 0.1, SC)

    # ---- room labels with clear sizes
    labels = {
        "KITCHEN / LIVING": (ft(12, 6), ft(28, 0)),
        "BEDROOM 1": (ft(14, 9), ft(20, 6)),
        "BEDROOM 2": (ft(13, 6), ft(7, 6)),
        "BATH 1": (ft(4, 4), ft(15, 9)),
        "BATH 2": (ft(4, 4), ft(6, 9)),
        "W.I.C.": (ft(2, 9), ft(1, 9)),
        "HALL": (ft(7, 7), ft(12, 3)),
    }
    for name, (cx, cy) in labels.items():
        small = name in ("BATH 1", "BATH 2", "W.I.C.", "LAUNDRY", "HALL")
        rot = 90 if name in ("HALL", "BATH 1", "BATH 2") else 0
        btext(blk, name, (cx, cy), 0.1 if small else 0.14, SC, rot=rot)
        if name in M.ROOMS and not small:
            w, h = clear(*M.ROOMS[name])
            btext(blk, f"{ft_in(w)} x {ft_in(h)}", (cx, cy - 0.24 / k), 0.09, SC)
            btext(blk, "CLG. HT. 9'-0\"", (cx, cy - 0.42 / k), 0.08, SC)

    # ---- fixtures detail additions
    for y0, y1 in [(M.Y_BATH_SPLIT, M.Y_LAUNDRY_S - ft(0, 4)), (M.Y_WIC_N, M.Y_BATH_SPLIT)]:
        # toilet + lav (simple outlines) below the shower
        tx, ty = E + ft(0, 2), y1 - ft(4, 9)
        rect(blk, tx, ty - ft(0, 9), tx + ft(0, 8), ty + ft(0, 9), "P-FIXT")                 # tank
        blk.add_ellipse((tx + ft(1, 6), ty), major_axis=(ft(0, 10), 0), ratio=0.7, dxfattribs={"layer": "P-FIXT"})
        lx, ly = E + ft(0, 1), y0 + ft(1, 6)
        rect(blk, lx, ly - ft(1, 0), lx + ft(1, 9), ly + ft(1, 0), "P-FIXT")                 # vanity
        blk.add_circle((lx + ft(0, 11), ly), ft(0, 6), dxfattribs={"layer": "P-FIXT"})
    # range burners, sink bowls, DW
    for dx in (ft(3, 9), ft(5, 9)):
        for dy in (L - ft(0, 11), L - ft(1, 11)):
            blk.add_circle((dx, dy), ft(0, 4), dxfattribs={"layer": "P-FIXT"})
    rect(blk, E + ft(0, 3), ft(29, 6), E + ft(1, 8), ft(31, 0), "P-FIXT")
    rect(blk, E + ft(0, 3), ft(31, 2), E + ft(1, 8), ft(32, 8), "P-FIXT")
    rect(blk, E, ft(26, 0), ft(2, 6), ft(28, 6), "P-FIXT")
    btext(blk, "DW", (ft(1, 5), ft(27, 3)), 0.07, SC)
    # attic access (dashed)
    blk.add_lwpolyline([(ft(6, 0), ft(19, 6)), (ft(8, 2), ft(19, 6)), (ft(8, 2), ft(22, 0)), (ft(6, 0), ft(22, 0))],
                       close=True, dxfattribs={"layer": "A-HIDN"})
    # alarms + fans
    for (x, y), t in [((ft(16, 6), ft(18, 0)), "S"), ((ft(15, 6), ft(4, 0)), "S"), ((ft(7, 2), ft(17, 9)), "S/CO"),
                      ((ft(15, 0), ft(30, 3)), "S/CO")]:
        blk.add_circle((x, y), 0.17 / k, dxfattribs={"layer": "E-LITE"})
        btext(blk, t, (x, y), 0.07 if "/" in t else 0.09, SC)
    for x, y in [(ft(3, 9), ft(18, 6)), (ft(3, 9), ft(8, 3))]:
        rect(blk, x - ft(0, 6), y - ft(0, 6), x + ft(0, 6), y + ft(0, 6), "M-HVAC")
        blk.add_line((x - ft(0, 6), y - ft(0, 6)), (x + ft(0, 6), y + ft(0, 6)), dxfattribs={"layer": "M-HVAC"})
        btext(blk, "EF", (x + ft(1, 0), y), 0.07, SC)
    # exterior equipment (dashed)
    for (x0, y0, x1, y1), t in [((ft(0, 4), L + ft(0, 3), ft(2, 10), L + ft(2, 9)), "HPWH"),
                                ((ft(4, 0), L, ft(5, 2), L + ft(0, 6)), "SP"),
                                ((W + ft(1, 0), ft(9, 0), W + ft(4, 0), ft(12, 0)), "HP")]:
        blk.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": "A-HIDN"})
        btext(blk, t, ((x0 + x1) / 2, (y0 + y1) / 2), 0.07, SC)
    # keynotes
    for n, at, to in KN_TAGS:
        if to:
            blk.add_line(at, to, dxfattribs={"layer": "A-ANNO"})
        hexa(blk, at, 0.15 / k, n)

    # ---- dimension strings
    o1, o2, o3 = ft(4, 0), ft(6, 3), ft(8, 6)
    def chain(pts, axis, side_off):
        for a, b in zip(pts, pts[1:]):
            if axis == "x":
                dim(blk, (a, side_off[0]), (b, side_off[0]), side_off[1], SC)
            else:
                dim(blk, (side_off[0], a), (side_off[0], b), side_off[1], SC)
    # west (left): openings, partitions, overall  (vertical dims; +offset = left)
    wwin = sorted([(a, b) for s, a, b, _ in M.WINDOWS if s == "W"])
    chain([0] + [v for ab in wwin for v in ab] + [L], "y", (0, o1))
    chain([0, M.Y_WIC_N, M.Y_BATH_SPLIT, M.Y_LAUNDRY_S - ft(0, 4), M.Y_KITCHEN_S, L], "y", (0, o2))
    dim(blk, (0, 0), (0, L), o3, SC)
    # east (right): openings, partitions, overall
    ewin = sorted([(a, b) for s, a, b, _ in M.WINDOWS if s == "E"])
    chain([0] + [v for ab in ewin for v in ab] + [L], "y", (W, -o1))
    chain([0, M.Y_BR_SPLIT, M.Y_KITCHEN_S, L], "y", (W, -o2))
    dim(blk, (W, 0), (W, L), -o3, SC)
    # north (top): door + window + porch
    a, w = M.ENTRY_DOOR[1], M.ENTRY_DOOR[2]
    nwin = [(a2, b2) for s, a2, b2, _ in M.WINDOWS if s == "N"][0]
    chain([0, a, a + w, nwin[0], nwin[1], W], "x", (L, ft(6, 6)))
    chain([0, M.PORCH[0], M.PORCH[1], W], "x", (L, ft(8, 9)))
    dim(blk, (0, L), (W, L), ft(11, 0), SC)
    # south (bottom)
    chain([0, M.X_BATH_E, W], "x", (0, -o1))
    dim(blk, (0, 0), (W, 0), -o2, SC)
    # interior: hall width, BR1 west wall
    dim(blk, (M.X_BATH_E, ft(16, 0)), (M.X_BR1_W, ft(16, 0)), 0, SC)


def schedule(msp, x, y, title, cols, widths, data):
    y = header(msp, x, y, sum(widths), title)
    cx = x
    for c, w in zip(cols, widths):
        text(msp, c, (cx + 0.08, y), h=0.1, layer="A-ANNO-TITL")
        cx += w
    msp.add_line((x, y - 0.1), (x + sum(widths), y - 0.1), dxfattribs={"layer": "A-ANNO"})
    y -= 0.32
    for row in data:
        cx = x
        for v, w in zip(row, widths):
            text(msp, v, (cx + 0.08, y), h=0.1)
            cx += w
        y -= 0.24
    rect(msp, x, y + 0.08, x + sum(widths), y + 0.24 * (len(data)) + 0.5, "A-ANNO")
    return y - 0.2


def build():
    s = new_sheet(NUMBER, TITLE)
    msp = s.msp
    xa, ya, xb, yb = s.drawing_area
    blk = new_drawing_block(s, "ADU_FLOOR_PLAN")
    draw(blk)
    k = SCALES[SC]
    ox, oy = xa + 4.0, ya + 3.3
    place_drawing(s, "ADU_FLOOR_PLAN", (ox, oy), SC, "ADU FLOOR PLAN", title_pos=(xa + 0.4, ya + 0.75), detail_no="1")
    north_arrow(msp, (ox + M.W * k + 3.4, oy + M.L * k + 1.0), size=0.8)

    # ---- right side: schedules + legend + notes
    rx = xa + 16.4
    y = yb - 0.3
    y = schedule(msp, rx, y, "DOOR SCHEDULE", ["NO.", "LOCATION", "SIZE (W x H)", "TYPE", "REMARKS"],
                 [0.55, 1.4, 1.6, 2.1, 5.0], DOORS)
    y = schedule(msp, rx, y - 0.1, "WINDOW SCHEDULE", ["MARK", "LOCATION", "SIZE (W x H)", "TYPE", "SILL A.F.F.", "REMARKS"],
                 [0.65, 1.3, 1.6, 1.3, 1.25, 4.55],
                 [(m,) + v for m, v in WINDOWS.items()])
    para(msp, rx, y + 0.05, [
        "ALL WINDOWS: VINYL FRAME, DUAL-GLAZED LOW-E; U-FACTOR / SHGC PER TITLE 24. SAFETY GLAZING PER CRC R308. "
        "BEDROOM EGRESS (CRC R310): NET CLEAR 5.7 SF MIN., 24\" MIN. H, 20\" MIN. W, SILL 44\" MAX. A.F.F.",
    ], 10.6)
    y -= 0.85

    w = 10.6
    y = header(msp, rx, y, w, "WALL LEGEND")
    rect(msp, rx + 0.15, y - 0.08, rx + 1.05, y + 0.06, "A-WALL")
    text(msp, "(N) EXTERIOR WALL: 4\" (PER OWNER) - 2x4 STUDS @ 16\" O.C. W/ INSULATION PER TITLE 24,", (rx + 1.25, y), h=0.11)
    text(msp, "EXTERIOR FINISH PER A4.0, 1/2\" GYP. BD. INTERIOR. SHEAR WALLS / HOLDOWNS PER STRUCTURAL.", (rx + 1.25, y - 0.2), h=0.11)
    y -= 0.5
    rect(msp, rx + 0.15, y - 0.06, rx + 1.05, y + 0.04, "A-WALL")
    text(msp, "(N) INTERIOR WALL: 2x4 STUDS @ 16\" O.C. W/ 1/2\" GYP. BD. EA. SIDE (5/8\" TYPE X WHERE REQ'D).", (rx + 1.25, y), h=0.11)
    y -= 0.45

    y = header(msp, rx, y, w, "FLOOR PLAN KEYNOTES")
    for n, note in enumerate(KEYNOTES, 1):
        cx, cy = rx + 0.25, y - 0.03
        msp.add_lwpolyline([(cx + 0.15 * math.cos(math.radians(a)), cy + 0.15 * math.sin(math.radians(a)))
                            for a in range(0, 360, 60)], close=True, dxfattribs={"layer": "A-ANNO"})
        text(msp, str(n), (cx, cy), h=0.1, align=TextEntityAlignment.MIDDLE_CENTER)
        y = para(msp, rx + 0.4, y + 0.04, [note], w - 0.4) - 0.08

    y = header(msp, rx, y - 0.1, w, "FLOOR PLAN NOTES / AREA")
    para(msp, rx, y, [
        f"1. ADU CONDITIONED AREA (TO OUTSIDE FACE OF STUD): {ft_in(M.W)} x {ft_in(M.L)} = {M.area_sqft():.0f} SF "
        "(800 SF MAX.). COVERED PORCH: 22 SF (NOT CONDITIONED).",
        "2. DIMENSIONS ARE TO OUTSIDE FACE OF STUD / FACE OF STUD UNLESS NOTED OTHERWISE.",
        "3. CEILING HEIGHT 9'-0\" TYP. - VERIFY WITH SECTIONS A5.0. ROOF PER A3.0, FRAMING PER STRUCTURAL.",
        "4. EXTERIOR EQUIPMENT LOCATIONS (HPWH, SUB-PANEL, HEAT PUMP) ARE COORDINATED WITH SITE PLAN A1.0.",
    ], w)
    return s
