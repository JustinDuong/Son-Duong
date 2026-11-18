"""Single source of truth for the ADU geometry (real inches).

Origin = SW outside corner of the ADU, +X east, +Y north (entry/porch on the north wall).
Traced from "Proposed Plan - Bee Cons - 14720 Hunter Ln 8-17-2026.pdf" (sheet A.00).
Stated dimensions are used where printed; the rest were measured from the PDF (about +/- 2").
"""
from plans.lib import ft

# ---- overall (outside face of framing)
W = ft(20, 2.25)        # E-W width  (printed 20'-2 1/4")
L = ft(38, 7.0625)      # N-S length (printed 38'-7 1/16")
EXT_T = 6.0             # exterior wall: 2x6 + finishes (assumed)
INT_T = 4.5             # interior wall: 2x4 + drywall

# ---- interior partition lines (inches from SW outside corner)
Y_KITCHEN_S = ft(24, 0)     # south edge of kitchen/living (wall stub + BR1 north wall)
X_BATH_E = ft(5, 6.5)       # east wall of bath column / west wall of BR2
X_BR1_W = ft(8, 9.5)        # west wall of bedroom 1 (hall is between)
Y_BR_SPLIT = ft(10, 4.5)    # wall between bedroom 1 (north) and bedroom 2 (south)
Y_LAUNDRY_S = ft(21, 2)     # laundry stack / bath 1 split
Y_BATH_SPLIT = ft(12, 4)    # bath 1 / bath 2 split
Y_WIC_N = ft(3, 11)         # walk-in closet / bath 2 split

# ---- rooms: name -> (x0, y0, x1, y1) clear-ish bounds for labels/areas
ROOMS = {
    "KITCHEN / LIVING": (0, Y_KITCHEN_S, W, L),
    "BEDROOM 1": (X_BR1_W, Y_BR_SPLIT, W, Y_KITCHEN_S),
    "BEDROOM 2": (X_BATH_E, 0, W, Y_BR_SPLIT),
    "BATH 1": (0, Y_BATH_SPLIT, X_BATH_E, Y_LAUNDRY_S - ft(0, 4)),
    "BATH 2": (0, Y_WIC_N, X_BATH_E, Y_BATH_SPLIT),
    "W.I.C.": (0, 0, X_BATH_E, Y_WIC_N),
    "LAUNDRY": (0, Y_LAUNDRY_S, X_BATH_E, Y_KITCHEN_S),
    "HALL": (X_BATH_E, Y_BR_SPLIT, X_BR1_W, Y_KITCHEN_S),
}

# ---- openings: (wall, start, end, tag)  wall = 'N','S','E','W' exterior; position along wall in inches
#   N/S walls measure along X from west; E/W walls measure along Y from south
WINDOWS = [
    ("N", ft(14, 6), ft(19, 6), "W 5040"),       # living room
    ("W", ft(28, 5), ft(33, 5), "W 5040"),       # kitchen (over sink)
    ("E", ft(26, 7), ft(35, 7), "SL 9068"),      # living slider
    ("E", ft(14, 9), ft(19, 9), "W 5040"),       # bedroom 1
    ("E", ft(2, 10), ft(7, 10), "W 5040"),       # bedroom 2
    ("W", ft(15, 4), ft(17, 4), "W 2010"),       # bath 1 (printed "2710")
    ("W", ft(7, 2), ft(9, 2), "W 2010"),         # bath 2 (printed "2710")
]
ENTRY_DOOR = ("N", ft(10, 0.1875), ft(3, 0), "3068")   # starts 10'-0 3/16" from west face
PORCH = (ft(8, 9), ft(14, 2), ft(4, 1))                # x0, x1, depth beyond north face (~22 sf)

# interior doors: (hinge_xy, width, angle_deg, swing, tag)
INT_DOORS = [
    ((X_BATH_E, ft(15, 0)), ft(2, 6), 270, -1, "2680"),   # hall -> bath 1
    ((X_BR1_W, ft(13, 4)), ft(2, 8), 270, 1, "2880"),     # hall -> bedroom 1
    ((ft(8, 6), Y_BR_SPLIT), ft(2, 6), 180, 1, "2680"),   # hall -> bedroom 2
    ((X_BATH_E, ft(4, 4)), ft(2, 6), 90, 1, "2680"),      # bedroom 2 -> bath 2
]
BARN_DOOR = (X_BATH_E, ft(0, 8), ft(3, 2), "2680 BARN")   # bedroom 2 -> W.I.C.

# ---- placement on the lot (lot coords: SW lot corner = 0,0, +X east toward Hunter Ln)
LOT_W_NS = ft(62, 2.4)       # 62.2 ft (OC GIS)
LOT_D_EW = ft(116, 0)
ADU_ORIGIN_ON_LOT = (ft(5, 0), ft(5, 0))   # 5'-0" from rear (west) and south side lines (scaled from proposed plan)


def area_sqft():
    return W * L / 144.0
