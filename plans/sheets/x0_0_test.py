"""X0.0 - Design base: the proposed ADU traced from the owner's plan, and placed on the
real lot from OC GIS. For review only (not part of the permit set)."""
import json


from plans import adu_model as M
from plans.adu_draw import btext, draw_adu
from plans.lib import (ROOT, dim, ft, ft_in, mtext, new_drawing_block, new_sheet, north_arrow,
                        place_drawing)

NUMBER, TITLE = "X0.0", "DESIGN BASE - TRACED PROPOSED PLAN (REVIEW ONLY)"
FP_SCALE = '1/4" = 1\'-0"'
SITE_SCALE = '1/8" = 1\'-0"'


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
                                  ((ft(36), ft(13), ft(48), ft(23)), "(E) SHED - TO BE REMOVED")]:
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
        "A. EXTERIOR WALLS 4\" (OWNER), INTERIOR 2x4.\\P"
        "B. ADU AT 5'-0\" FROM REAR AND SOUTH SIDE LINES (SCALED FROM REFERENCE). "
        "UNDER 5' WOULD REQUIRE FIRE SPRINKLERS.\\P"
        "C. (E) SHED TO BE REMOVED (OWNER)."
    )
    mtext(s.msp, notes, (11.2, 9.9), h=0.12, width=17.5)
    return s
