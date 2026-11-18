"""Shared drawing toolkit for the construction plan set.

Conventions
-----------
* Each sheet is one DXF file drawn in model space in **paper inches**
  (ARCH D, 36" wide x 24" tall). Origin = lower-left corner of the sheet.
* Building geometry is drawn at **real size in inches** inside a block,
  then placed on the sheet with `place_drawing(...)` at a plot scale
  (e.g. 1/4" = 1'-0"  ->  scale = 1/48). This keeps the DXF usable in CAD
  while the PDF prints at true scale.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment

ROOT = Path(__file__).resolve().parent.parent
PROJECT = json.loads((ROOT / "project.json").read_text())

SHEET_W, SHEET_H = 36.0, 24.0
BORDER = 0.5            # border offset from sheet edge (left edge gets binding margin)
BIND = 1.5              # binding margin on left side
TB_W = 3.5              # title block width (right side strip)

# Common architectural scales: name -> factor (paper inches per real inch)
SCALES = {
    '1" = 1\'-0"': 1 / 12,
    '3/4" = 1\'-0"': 1 / 16,
    '1/2" = 1\'-0"': 1 / 24,
    '3/8" = 1\'-0"': 1 / 32,
    '1/4" = 1\'-0"': 1 / 48,
    '3/16" = 1\'-0"': 1 / 64,
    '1/8" = 1\'-0"': 1 / 96,
    '1" = 10\'': 1 / 120,
    '1" = 20\'': 1 / 240,
}

# layer name -> (ACI color, lineweight in 1/100 mm, linetype)
LAYERS = {
    "A-BORDER":    (7, 70, "CONTINUOUS"),
    "A-TTLB":      (7, 35, "CONTINUOUS"),
    "A-WALL":      (7, 50, "CONTINUOUS"),
    "A-WALL-HTCH": (8, 13, "CONTINUOUS"),
    "A-DOOR":      (7, 25, "CONTINUOUS"),
    "A-GLAZ":      (7, 25, "CONTINUOUS"),
    "A-DIMS":      (7, 18, "CONTINUOUS"),
    "A-ANNO":      (7, 25, "CONTINUOUS"),
    "A-ANNO-TITL": (7, 50, "CONTINUOUS"),
    "A-GRID":      (8, 18, "CENTER"),
    "A-HIDN":      (8, 18, "HIDDEN"),
    "C-PROP":      (7, 50, "PHANTOM"),
    "C-SETB":      (8, 25, "DASHED"),
    "S-FNDN":      (7, 50, "CONTINUOUS"),
    "S-FRAM":      (7, 35, "CONTINUOUS"),
    "E-POWR":      (7, 25, "CONTINUOUS"),
    "E-LITE":      (7, 25, "CONTINUOUS"),
    "P-FIXT":      (7, 25, "CONTINUOUS"),
    "M-HVAC":      (7, 25, "CONTINUOUS"),
}


@dataclass
class Sheet:
    number: str          # e.g. "A1.0"
    title: str           # e.g. "SITE PLAN"
    doc: ezdxf.document.Drawing
    msp: object

    @property
    def drawing_area(self):
        """(xmin, ymin, xmax, ymax) usable area inside the border, left of title block."""
        return (BIND + 0.25, BORDER + 0.25, SHEET_W - BORDER - TB_W - 0.25, SHEET_H - BORDER - 0.25)

    def save(self, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{self.number}.dxf"
        self.doc.saveas(path)
        return path


# --------------------------------------------------------------------------- setup
def new_sheet(number: str, title: str) -> Sheet:
    doc = ezdxf.new("R2018", setup=True, units=ezdxf.units.IN)
    doc.header["$LTSCALE"] = 0.5
    for name, (color, lw, lt) in LAYERS.items():
        doc.layers.add(name, color=color, linetype=lt, lineweight=lw)
    if "ARCH" not in doc.styles:
        doc.styles.add("ARCH", font="arial.ttf")
    sheet = Sheet(number, title, doc, doc.modelspace())
    _border_and_title_block(sheet)
    return sheet


def text(msp, s, pos, h=0.125, layer="A-ANNO", align=TextEntityAlignment.LEFT, rot=0.0):
    t = msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "ARCH"})
    t.set_placement(pos, align=align)
    return t


def mtext(msp, s, pos, h=0.11, width=None, layer="A-ANNO"):
    m = msp.add_mtext(s, dxfattribs={"layer": layer, "style": "ARCH", "char_height": h})
    m.set_location(pos, attachment_point=ezdxf.enums.MTextEntityAlignment.TOP_LEFT)
    if width:
        m.dxf.width = width
    return m


def rect(msp, x0, y0, x1, y1, layer):
    return msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True,
                              dxfattribs={"layer": layer})


def _border_and_title_block(sheet: Sheet):
    msp, P = sheet.msp, PROJECT
    x0, y0, x1, y1 = BIND, BORDER, SHEET_W - BORDER, SHEET_H - BORDER
    rect(msp, x0, y0, x1, y1, "A-BORDER")
    tx = x1 - TB_W
    msp.add_line((tx, y0), (tx, y1), dxfattribs={"layer": "A-BORDER"})

    # Title block rows, top to bottom: (label, value, row height)
    rows = [
        ("PROJECT", P["project_name"], 1.6),
        ("ADDRESS", P["project_address"], 1.2),
        ("APN", P["apn"], 0.6),
        ("OWNER", P["owner"], 0.8),
        ("PREPARED BY", P["designer"], 1.0),
        ("PROFESSIONAL STAMP", "", 3.0),
        ("REVISIONS", f"REV {P['revision']}", 2.4),
        ("DATE", P["date"], 0.6),
    ]
    y = y1
    for label, value, h in rows:
        y -= h
        msp.add_line((tx, y), (x1, y), dxfattribs={"layer": "A-TTLB"})
        text(msp, label, (tx + 0.1, y + h - 0.18), h=0.08, layer="A-TTLB")
        if value:
            mtext(msp, value, (tx + 0.1, y + h - 0.3), h=0.12, width=TB_W - 0.2, layer="A-TTLB")
    # Sheet title + number at the bottom
    text(msp, "SHEET TITLE", (tx + 0.1, y - 0.18), h=0.08, layer="A-TTLB")
    mtext(msp, sheet.title, (tx + 0.1, y - 0.35), h=0.2, width=TB_W - 0.2, layer="A-ANNO-TITL")
    sy = y0 + 1.6
    msp.add_line((tx, sy), (x1, sy), dxfattribs={"layer": "A-TTLB"})
    text(msp, "SHEET", (tx + 0.1, sy - 0.18), h=0.08, layer="A-TTLB")
    text(msp, sheet.number, (tx + TB_W / 2, y0 + 0.55), h=0.6, layer="A-ANNO-TITL",
         align=TextEntityAlignment.MIDDLE_CENTER)


# --------------------------------------------------------------------------- placing drawings
def new_drawing_block(sheet: Sheet, name: str):
    """Create a block to draw real-size geometry (inches) into."""
    return sheet.doc.blocks.new(name=name)


def place_drawing(sheet: Sheet, block_name: str, insert, scale_name: str,
                  title: str, title_pos=None, detail_no: str = "1"):
    """Insert a real-size block on the sheet at the given scale and add a drawing title."""
    k = SCALES[scale_name]
    sheet.msp.add_blockref(block_name, insert, dxfattribs={"xscale": k, "yscale": k, "layer": "0"})
    if title_pos is not None:
        drawing_title(sheet.msp, title_pos, detail_no, title, scale_name)


def drawing_title(msp, pos, no, title, scale_name):
    x, y = pos
    msp.add_circle((x + 0.3, y), 0.3, dxfattribs={"layer": "A-ANNO-TITL"})
    text(msp, no, (x + 0.3, y + 0.08), h=0.14, layer="A-ANNO-TITL", align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_line((x + 0.6, y), (x + 5.0, y), dxfattribs={"layer": "A-ANNO-TITL"})
    text(msp, title.upper(), (x + 0.7, y + 0.07), h=0.2, layer="A-ANNO-TITL")
    text(msp, f"SCALE: {scale_name}", (x + 0.7, y - 0.2), h=0.1)


# --------------------------------------------------------------------------- real-size helpers
def ft(feet: float, inches: float = 0.0) -> float:
    """Feet + inches -> inches."""
    return feet * 12 + inches


def ft_in(inches: float, precision: int = 2) -> str:
    """Format inches as architectural feet-inches, e.g. 150.5 -> 12'-6 1/2"."""
    q = round(inches * precision) / precision
    f, i = divmod(q, 12)
    whole, frac = int(i), i - int(i)
    frac_s = ""
    if frac:
        from fractions import Fraction
        frac_s = " " + str(Fraction(frac).limit_denominator(16))
    return f"{int(f)}'-{whole}{frac_s}\""


def wall(blk, p1, p2, thickness=ft(0, 4.5), layer="A-WALL"):
    """Draw a wall as two parallel lines centered on p1->p2 (real inches)."""
    import math
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / L * thickness / 2, (x2 - x1) / L * thickness / 2
    pts = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
    blk.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})


def dim(blk, p1, p2, offset, scale_name, angle=None, layer="A-DIMS"):
    """Linear dimension in real units; text sized for the plot scale (3/32" on paper)."""
    k = SCALES[scale_name]
    import math
    if angle is None:
        angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
    rad = math.radians(angle + 90)
    mid = ((p1[0] + p2[0]) / 2 + math.cos(rad) * offset, (p1[1] + p2[1]) / 2 + math.sin(rad) * offset)
    a = math.radians(angle)
    length = abs((p2[0] - p1[0]) * math.cos(a) + (p2[1] - p1[1]) * math.sin(a))
    d = blk.add_linear_dim(base=mid, p1=p1, p2=p2, angle=angle, dimstyle="Standard", text=ft_in(length),
                           override={"dimtxt": 0.09375 / k, "dimasz": 0.09375 / k, "dimexo": 0.0625 / k,
                                     "dimexe": 0.0625 / k, "dimgap": 0.04 / k, "dimtsz": 0.05 / k,
                                     "dimlunit": 4, "dimzin": 3, "dimtad": 1, "dimtih": 0, "dimtoh": 0},
                           dxfattribs={"layer": layer})
    d.render()
    return d


def door(blk, hinge, width, angle_deg=0, swing=1, layer="A-DOOR"):
    """Plan door: leaf line + 90 deg swing arc. hinge in real inches, width in inches."""
    import math
    a = math.radians(angle_deg)
    end = (hinge[0] + width * math.cos(a), hinge[1] + width * math.sin(a))
    leaf = (hinge[0] + width * math.cos(a + swing * math.pi / 2), hinge[1] + width * math.sin(a + swing * math.pi / 2))
    blk.add_line(hinge, leaf, dxfattribs={"layer": layer})
    s, e = (angle_deg, angle_deg + 90) if swing > 0 else (angle_deg - 90, angle_deg)
    blk.add_arc(hinge, width, s, e, dxfattribs={"layer": layer})
    return end


def window(blk, p1, p2, wall_t=ft(0, 4.5), layer="A-GLAZ"):
    """Plan window: three parallel lines across the wall thickness."""
    import math
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    for o in (-wall_t / 2, -wall_t / 6, wall_t / 6, wall_t / 2):
        blk.add_line((x1 + nx * o, y1 + ny * o), (x2 + nx * o, y2 + ny * o), dxfattribs={"layer": layer})
    for (px, py) in ((x1, y1), (x2, y2)):  # jambs
        blk.add_line((px - nx * wall_t / 2, py - ny * wall_t / 2), (px + nx * wall_t / 2, py + ny * wall_t / 2),
                     dxfattribs={"layer": layer})


def north_arrow(msp, pos, size=0.6):
    x, y = pos
    msp.add_circle((x, y), size / 2, dxfattribs={"layer": "A-ANNO"})
    msp.add_solid([(x, y + size / 2), (x - size / 6, y - size / 4), (x, y - size / 8)],
                  dxfattribs={"layer": "A-ANNO"})
    msp.add_lwpolyline([(x, y + size / 2), (x + size / 6, y - size / 4), (x, y - size / 8)], close=True,
                       dxfattribs={"layer": "A-ANNO"})
    text(msp, "N", (x, y + size / 2 + 0.15), h=0.2, align=TextEntityAlignment.MIDDLE_CENTER)
