"""X0.0 - Toolkit test sheet (not part of the permit set).
Draws a sample 20'x14' room at 1/4"=1'-0" to verify scale, walls, doors, windows, dims."""
from plans.lib import new_sheet, new_drawing_block, place_drawing, wall, door, window, dim, ft, north_arrow

NUMBER, TITLE = "X0.0", "TOOLKIT TEST (NOT FOR SUBMITTAL)"
SCALE = '1/4" = 1\'-0"'


def build():
    s = new_sheet(NUMBER, TITLE)
    blk = new_drawing_block(s, "TEST_PLAN")
    W, H = ft(20), ft(14)
    for a, b in [((0, 0), (W, 0)), ((W, 0), (W, H)), ((W, H), (0, H)), ((0, H), (0, 0))]:
        wall(blk, a, b)
    door(blk, (ft(3), 0), ft(3), angle_deg=0, swing=1)
    window(blk, (ft(12), H), (ft(16), H))
    dim(blk, (0, 0), (W, 0), offset=-ft(3), scale_name=SCALE)
    dim(blk, (W, 0), (W, H), offset=-ft(3), scale_name=SCALE)
    place_drawing(s, "TEST_PLAN", (6, 8), SCALE, "TEST ROOM PLAN", title_pos=(6, 6))
    north_arrow(s.msp, (20, 18))
    return s
