"""Shared drawing routines for the ADU (real-size, inches) used by several sheets."""
from ezdxf.enums import TextEntityAlignment

from plans import adu_model as M
from plans.lib import SCALES, dim, door, ft, rect, wall, window


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
