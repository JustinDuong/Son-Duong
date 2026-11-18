"""A0.0 - Cover sheet: project data, scope, code basis, sheet index."""
from plans.lib import PROJECT, new_sheet, text, mtext
from plans.sheet_index import SHEET_INDEX

NUMBER, TITLE = "A0.0", "COVER SHEET"


def build():
    s = new_sheet(NUMBER, TITLE)
    msp, P = s.msp, PROJECT
    x0, y0, x1, y1 = s.drawing_area

    text(msp, P["project_name"], (x0 + 0.5, y1 - 1.0), h=0.6, layer="A-ANNO-TITL")
    text(msp, P["project_address"], (x0 + 0.5, y1 - 1.6), h=0.3)

    # Project data
    yy = y1 - 3.0
    text(msp, "PROJECT DATA", (x0 + 0.5, yy), h=0.22, layer="A-ANNO-TITL")
    data = [("OWNER", P["owner"]), ("APN", P["apn"]), ("JURISDICTION", P["jurisdiction"]),
            ("ZONING", P.get("zoning", "")), ("GENERAL PLAN", P.get("general_plan", "")),
            ("LOT AREA", P.get("lot_area", "")), ("TRACT", P.get("tract", "")),
            ("CODE BASIS", P["code_basis"]), ("OCCUPANCY", P["occupancy"]),
            ("CONSTRUCTION TYPE", P["construction_type"])]
    for i, (k, v) in enumerate(data):
        text(msp, f"{k}:", (x0 + 0.5, yy - 0.5 - i * 0.35), h=0.14)
        text(msp, v, (x0 + 3.2, yy - 0.5 - i * 0.35), h=0.14)

    yy -= 0.9 + len(data) * 0.35
    text(msp, "SCOPE OF WORK", (x0 + 0.5, yy), h=0.22, layer="A-ANNO-TITL")
    mtext(msp, P["scope_of_work"], (x0 + 0.5, yy - 0.35), h=0.14, width=12)

    # Sheet index
    ix = x0 + 16
    text(msp, "SHEET INDEX", (ix, y1 - 3.0), h=0.22, layer="A-ANNO-TITL")
    for i, (num, title) in enumerate(SHEET_INDEX):
        y = y1 - 3.5 - i * 0.3
        text(msp, num, (ix, y), h=0.14)
        text(msp, title, (ix + 1.2, y), h=0.14)

    mtext(msp, "THESE DRAWINGS ARE NOT VALID FOR PERMIT OR CONSTRUCTION UNTIL REVIEWED, "
               "SIGNED AND STAMPED BY A LICENSED PROFESSIONAL WHERE REQUIRED BY THE JURISDICTION.",
          (x0 + 0.5, y0 + 1.2), h=0.14, width=16)
    return s
