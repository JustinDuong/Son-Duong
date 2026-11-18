# Son-Duong — Construction Plan Set

Construction drawings generated from code, as CAD (DXF) and PDF files on 24"×36" (ARCH D) sheets.

## Setup (one time)

```bash
pip install -r requirements.txt
```

## Build the plans

```bash
python build.py            # all sheets
python build.py A0.0 A2.0  # selected sheets
```

Output:

| File | Use |
|---|---|
| `output/dxf/<sheet>.dxf` | CAD file. Open in AutoCAD, DWG TrueView (free) or LibreCAD (free) |
| `output/pdf/<sheet>.pdf` | One sheet, prints at true scale on 24×36 paper |
| `output/PlanSet.pdf` | Full set in sheet-index order, ready to submit |

## Project layout

| Path | What it is |
|---|---|
| `project.json` | Project info shown on every title block (name, address, APN, owner…) |
| `plans/sheet_index.py` | Master list of sheets in the set |
| `plans/lib.py` | Drawing toolkit: title block, layers, scales, walls, doors, windows, dimensions |
| `plans/sheets/*.py` | One file per sheet |

Sheets prefixed `X` are internal test sheets and are left out of `PlanSet.pdf`.

> These drawings must be reviewed and stamped by a licensed professional where the jurisdiction requires it before permit submittal.
