"""Build the plan set.

    python build.py            # build all sheets in the index -> output/
    python build.py A0.0 X0.0  # build only these sheets

Outputs:
    output/dxf/<sheet>.dxf     CAD files (open in AutoCAD, DWG TrueView, LibreCAD)
    output/pdf/<sheet>.pdf     24x36 PDF per sheet, true scale
    output/PlanSet.pdf         all permit sheets combined in index order
"""
import importlib
import pkgutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy, LineweightPolicy
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from pypdf import PdfWriter

import plans.sheets
from plans.lib import SHEET_W, SHEET_H
from plans.sheet_index import SHEET_INDEX

OUT = Path(__file__).resolve().parent / "output"


def discover():
    mods = {}
    for m in pkgutil.iter_modules(plans.sheets.__path__):
        mod = importlib.import_module(f"plans.sheets.{m.name}")
        if hasattr(mod, "NUMBER") and hasattr(mod, "build"):
            mods[mod.NUMBER] = mod
    return mods


def to_pdf(doc, path: Path):
    fig = plt.figure(figsize=(SHEET_W, SHEET_H))
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(color_policy=ColorPolicy.BLACK, background_policy=BackgroundPolicy.WHITE,
                        lineweight_policy=LineweightPolicy.ABSOLUTE)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace(), finalize=False)
    ax.set_xlim(0, SHEET_W)
    ax.set_ylim(0, SHEET_H)
    ax.set_aspect("equal")
    ax.axis("off")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf")
    plt.close(fig)


def main(only):
    mods = discover()
    targets = only or list(mods)
    built = {}
    for num in targets:
        if num not in mods:
            print(f"  ! {num}: no sheet module found")
            continue
        sheet = mods[num].build()
        sheet.save(OUT / "dxf")
        pdf = OUT / "pdf" / f"{num}.pdf"
        to_pdf(sheet.doc, pdf)
        built[num] = pdf
        print(f"  ✓ {num}  {sheet.title}")

    writer = PdfWriter()
    missing = []
    for num, _ in SHEET_INDEX:
        pdf = OUT / "pdf" / f"{num}.pdf"
        if pdf.exists():
            writer.append(str(pdf))
        else:
            missing.append(num)
    if writer.pages:
        writer.write(str(OUT / "PlanSet.pdf"))
        print(f"\nPlan set -> {OUT / 'PlanSet.pdf'} ({len(writer.pages)} sheets)")
    if missing:
        print("Not yet drawn:", ", ".join(missing))


if __name__ == "__main__":
    main(sys.argv[1:])
