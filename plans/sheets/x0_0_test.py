"""X0.0 - Design base: the proposed ADU traced from the owner's plan, and placed on the
real lot from OC GIS. For review only (not part of the permit set)."""
import json

from ezdxf.enums import TextEntityAlignment

from plans import adu_model as M
from plans.lib import (ROOT, SCALES, dim, door, drawing_title, ft, ft_in, mtext, new_drawing_block,
                       new_sheet, north_arrow, place_drawing, rect, text, wall, window)

NUMBER, TITLE = "X0.0", "DESIGN BASE - TRACED PROPOSED PLAN (REVIEW ONLY)"
FP_SCALE = '1/4" = 1\'-0"'
SITE_SCALE = '1/8" = 1\'-0"'


def btext(blk, s, pos, paper_h, scale, align=TextEntityAlignment.MIDDLE_CENTER, rot=0, layer="A-ANNO"):
    """Text inside a real-size block, sized to print at paper_h inches."""
    t = blk.add_text(s, height=paper_h / SCALES[scale], rotation=rot, dxfattribs={"layer": layer, "style": "ARCH"})
    t.set_placement(pos, align=align)


def opening_pts(side, a, b):
    if side == "N":
        return (a, M.L - M.EXT_T / 2), (b, M.L - M.EXT_T / 2)
    if side == "S":
        return (a, M.EXT_T / 2), (b, M.EXT_T / 2)
    if side == "E":
        return (M.W - M.EXT_T / 2, a), (M.W - M.EXT_T / 2, b)
    return (M.EXT_T / 2, a), (M.EXT_T / 2, b)


def draw_adu(blk, scale, detail=True):
    W, L, e, i = M.W, M.L, M.EXT_T, M.INT_T
    h = e / 2
    # exterior walls (centerlines inset by half thickness so outside faces land on W x L)
    corners = [(h, h), (W - h, h), (W - h, L - h), (h, L - h)]
    for k in range(4):
        wall(blk, corners[k], corners[(k + 1) % 4], e)
    # porch
    x0, x1, d = M.PORCH
    blk.add_lwpolyline([(x0, L), (x0, L + d), (x1, L + d), (x1, L)], dxfattribs={"layer": "A-WALL"})
    if not detail:
        btext(blk, "(N) ADU", (W / 2, L / 2 + ft(3)), 0.12, scale)
        btext(blk, f"{M.area_sqft():.0f} SF", (W / 2, L / 2 - ft(2)), 0.1, scale)
        return
    # interior walls
    for p1, p2 in [
        ((e, M.Y_KITCHEN_S), (ft(5, 10), M.Y_KITCHEN_S)),                # laundry/kitchen stub
        ((M.X_BR1_W, M.Y_KITCHEN_S), (W - e, M.Y_KITCHEN_S)),           # BR1 north wall
        ((M.X_BR1_W, M.Y_BR_SPLIT), (M.X_BR1_W, M.Y_KITCHEN_S)),        # BR1 west wall
        ((M.X_BATH_E, M.Y_BR_SPLIT), (W - e, M.Y_BR_SPLIT)),            # BR1/BR2
        ((M.X_BATH_E, e), (M.X_BATH_E, M.Y_LAUNDRY_S - ft(0, 4))),      # bath column east wall
        ((e, M.Y_LAUNDRY_S - ft(0, 4)), (M.X_BATH_E, M.Y_LAUNDRY_S - ft(0, 4))),
        ((e, M.Y_BATH_SPLIT), (M.X_BATH_E, M.Y_BATH_SPLIT)),
        ((e, M.Y_WIC_N), (M.X_BATH_E, M.Y_WIC_N)),
    ]:
        wall(blk, p1, p2, i)
    # windows + tags
    for side, a, b, tag in M.WINDOWS:
        p1, p2 = opening_pts(side, a, b)
        window(blk, p1, p2, e)
        mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        off = {"N": (0, ft(1, 3)), "S": (0, -ft(1, 3)), "E": (ft(1, 3), 0), "W": (-ft(1, 3), 0)}[side]
        btext(blk, tag, (mid[0] + off[0], mid[1] + off[1]), 0.07, scale, rot=90 if side in "EW" else 0)
    # entry door
    _, a, w, tag = M.ENTRY_DOOR
    door(blk, (a, L - e), w, angle_deg=0, swing=-1)
    btext(blk, tag, (a + w / 2, L - ft(3, 6)), 0.07, scale)
    # interior doors
    for hinge, w, ang, sw, tag in M.INT_DOORS:
        door(blk, hinge, w, angle_deg=ang, swing=sw)
    bx, by, bw, tag = M.BARN_DOOR
    blk.add_lwpolyline([(bx + 2, by), (bx + 2, by + bw), (bx + 4, by + bw), (bx + 4, by)], close=True,
                       dxfattribs={"layer": "A-DOOR"})
    btext(blk, "BARN", (bx + ft(0, 9), by + bw / 2), 0.06, scale, rot=90)
    # fixtures (simple outlines)
    fx = blk.add_lwpolyline
    fx([(e, L - e), (ft(8, 0), L - e), (ft(8, 0), L - ft(2, 6)), (ft(2, 6), L - ft(2, 6)),
        (ft(2, 6), ft(27, 0)), (e, ft(27, 0))], dxfattribs={"layer": "A-ANNO"})              # L-counter
    rect(blk, e, M.Y_KITCHEN_S + 2, ft(3, 0), M.Y_KITCHEN_S + ft(3, 0), "A-ANNO")             # REF
    btext(blk, "REF", (ft(1, 9), M.Y_KITCHEN_S + ft(1, 6)), 0.06, scale)
    btext(blk, "RANGE", (ft(5, 0), L - ft(1, 6)), 0.06, scale)
    btext(blk, "SINK", (ft(1, 6), ft(30, 11)), 0.06, scale, rot=90)
    btext(blk, "W/D STACK", (ft(1, 9), (M.Y_LAUNDRY_S + M.Y_KITCHEN_S) / 2), 0.06, scale)
    for y0, y1 in [(M.Y_BATH_SPLIT, M.Y_LAUNDRY_S - ft(0, 4)), (M.Y_WIC_N, M.Y_BATH_SPLIT)]:
        rect(blk, e, y1 - ft(3, 0), M.X_BATH_E - i / 2, y1 - i / 2, "A-ANNO")                  # shower
        blk.add_line((e, y1 - ft(3, 0)), (M.X_BATH_E - i / 2, y1 - i / 2), dxfattribs={"layer": "A-ANNO"})
        blk.add_line((e, y1 - i / 2), (M.X_BATH_E - i / 2, y1 - ft(3, 0)), dxfattribs={"layer": "A-ANNO"})
    # room labels
    for name, (x0, y0, x1, y1) in M.ROOMS.items():
        if name in ("HALL", "LAUNDRY"):
            continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if name == "KITCHEN / LIVING":
            cx += ft(3)
        rot = 90 if (x1 - x0) < ft(6) else 0
        btext(blk, name, (cx, cy), 0.1, scale, rot=rot)
    # dimensions
    dim(blk, (0, 0), (W, 0), -ft(4), scale)
    dim(blk, (W, 0), (W, L), -ft(4), scale)
    dim(blk, (W, 0), (W, M.Y_BR_SPLIT), -ft(2, 3), scale)
    dim(blk, (W, M.Y_BR_SPLIT), (W, M.Y_KITCHEN_S), -ft(2, 3), scale)
    dim(blk, (W, M.Y_KITCHEN_S), (W, L), -ft(2, 3), scale)
    dim(blk, (0, L), (M.ENTRY_DOOR[1], L), ft(6), scale)
    dim(blk, (0, 0), (M.X_BATH_E, 0), -ft(2, 3), scale)
    dim(blk, (M.X_BATH_E, 0), (W, 0), -ft(2, 3), scale)


def draw_site(blk, scale):
    LW, LD = M.LOT_D_EW, M.LOT_W_NS
    blk.add_lwpolyline([(0, 0), (LW, 0), (LW, LD), (0, LD)], close=True, dxfattribs={"layer": "C-PROP"})
    gis = json.loads((ROOT / "research" / "site_gis.json").read_text())
    fp = [(x * 12, y * 12) for x, y in gis["existing_footprint_gis_ft"]]
    blk.add_lwpolyline(fp, close=True, dxfattribs={"layer": "A-WALL"})
    btext(blk, "(E) HOUSE", (ft(74), ft(30)), 0.12, scale)
    btext(blk, "1-STORY, 1,011 SF LIVING", (ft(74), ft(25)), 0.08, scale)
    # structures seen on aerial (approximate)
    for (x0, y0, x1, y1), lab in [((ft(42), ft(23), ft(56.4), ft(42)), "(E) PATIO COVER (APPROX.)"),
                                  ((ft(36), ft(13), ft(48), ft(23)), "(E) SHED? (APPROX.)")]:
        blk.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": "A-HIDN"})
        btext(blk, lab, ((x0 + x1) / 2, (y0 + y1) / 2), 0.06, scale)
    # ADU (outline only)
    ox, oy = M.ADU_ORIGIN_ON_LOT
    sub = blk.doc.blocks.get("ADU_OUTLINE") or blk.doc.blocks.new("ADU_OUTLINE")
    if not len(sub):
        draw_adu(sub, scale, detail=False)
    blk.add_blockref("ADU_OUTLINE", (ox, oy))
    # setbacks (required 4' side/rear for ADU; R1: 20' front, 5' side, 25' rear)
    blk.add_lwpolyline([(ft(4), ft(4)), (LW - ft(20), ft(4)), (LW - ft(20), LD - ft(4)), (ft(4), LD - ft(4))],
                       close=True, dxfattribs={"layer": "C-SETB"})
    btext(blk, "4'-0\" ADU SETBACK LINE", (ft(30), ft(2.2)), 0.06, scale)
    # dimensions
    dim(blk, (0, 0), (LW, 0), -ft(6), scale)
    dim(blk, (0, 0), (0, LD), ft(6), scale)
    dim(blk, (0, oy + ft(10)), (ox, oy + ft(10)), 0, scale)
    dim(blk, (ox + ft(14), 0), (ox + ft(14), oy), 0, scale)
    dim(blk, (ox + ft(14), oy + M.L), (ox + ft(14), LD), 0, scale)
    dim(blk, (ox + M.W, ft(32)), (ft(42), ft(32)), 0, scale)
    # street
    blk.add_line((LW + ft(24.5), -ft(8)), (LW + ft(24.5), LD + ft(8)), dxfattribs={"layer": "A-GRID"})
    btext(blk, "HUNTER LN (C/L)", (LW + ft(27), LD / 2), 0.1, scale, rot=90)


def build():
    s = new_sheet(NUMBER, TITLE)
    fp = new_drawing_block(s, "ADU_FP")
    draw_adu(fp, FP_SCALE)
    place_drawing(s, "ADU_FP", (3.0, 3.6), FP_SCALE, "ADU FLOOR PLAN (TRACED)", title_pos=(2.2, 1.6), detail_no="1")

    site = new_drawing_block(s, "SITE")
    draw_site(site, SITE_SCALE)
    place_drawing(s, "SITE", (11.2, 13.2), SITE_SCALE, "ADU LOCATION ON LOT (GIS)", title_pos=(11.2, 11.0),
                  detail_no="2")
    north_arrow(s.msp, (28.6, 20.6))

    notes = (
        "HOW TO READ THIS SHEET\\P"
        "1. DRAWING 1 IS YOUR PROPOSED FLOOR PLAN, TRACED FROM 'PROPOSED PLAN - BEE CONS - 8-17-2026'. "
        "PRINTED DIMENSIONS WERE USED; OTHERS WERE MEASURED FROM THE PDF (+/- 2\").\\P"
        "2. DRAWING 2 PLACES THE ADU ON THE REAL LOT (62.2' x 116', OC GIS). HOUSE FOOTPRINT FROM OC GIS; "
        "PATIO COVER AND SHED ARE APPROXIMATE FROM THE AERIAL PHOTO.\\P"
        f"3. OUTSIDE AREA FROM PRINTED DIMS = {ft_in(M.W)} x {ft_in(M.L)} = {M.area_sqft():.0f} SF "
        "(REFERENCE PLAN SAYS 799 / 800 SF).\\P"
        "ITEMS TO CONFIRM\\P"
        "A. EXTERIOR WALLS ASSUMED 2x6 (6\"), INTERIOR 2x4.\\P"
        "B. ADU AT 5'-0\" FROM REAR AND SOUTH SIDE LINES (SCALED FROM REFERENCE). "
        "UNDER 5' WOULD REQUIRE FIRE SPRINKLERS.\\P"
        "C. IS THE SHED STAYING OR REMOVED?"
    )
    mtext(s.msp, notes, (11.2, 9.9), h=0.12, width=17.5)
    return s
