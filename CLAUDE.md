# CLAUDE.md — Son-Duong Construction Plan Set

## Goal
Produce a complete, permit-ready construction drawing set (24"×36" ARCH D) as DXF + PDF,
combined into `output/PlanSet.pdf`. Final set is reviewed/stamped by a licensed professional
before submittal — Claude prepares the drawings, it does not certify them.

## Commands
- Install: `pip install -r requirements.txt` (the Son-Duong cloud environment does this automatically)
- Build all: `python build.py` · Build some: `python build.py A1.0 A2.0`
- Visual check: `pdftoppm -r 40 -png output/pdf/<sheet>.pdf <scratch>/img` and look at the image.
  Always render and inspect a sheet after changing it.

## Structure
- `project.json` — single source of project facts (title block + cover sheet). Update here, never hard-code.
- `plans/sheet_index.py` — master sheet list; order = order in PlanSet.pdf.
- `plans/lib.py` — toolkit: `new_sheet`, `new_drawing_block`, `place_drawing`, `wall`, `door`,
  `window`, `dim`, `ft`, `ft_in`, `text`, `mtext`, `north_arrow`, `SCALES`, `LAYERS`.
- `plans/sheets/<a1_0_site>.py` — one module per sheet; must define `NUMBER`, `TITLE`, `build()`
  returning a `Sheet`. Auto-discovered by `build.py`.
- `X*` sheets are internal tests and are never in the index / PlanSet.

## Drawing conventions
- Sheet space is paper inches, origin lower-left, 36 wide × 24 tall. Keep content inside
  `sheet.drawing_area` (title block strip on the right).
- Building geometry is drawn **real size in inches** inside a block (`ft(12, 6)` = 12'-6"),
  then placed with `place_drawing(..., scale_name)`. Never draw pre-scaled geometry.
- Scales: plans/elevations/sections 1/4"=1'-0"; site plan 1"=10' or 1"=20' (fit lot);
  roof 1/4" or 1/8"; details 3/4" to 1-1/2"=1'-0".
- Dimensions in feet-inches (`ft_in`), text 3/32" on paper; drawing titles via `drawing_title`.
- Use the AIA-style layers in `LAYERS` (A-, C-, S-, E-, P-, M- prefixes); add new ones there.
- All annotation text UPPERCASE.
- Every sheet: drawing title + scale under each view; north arrow on plan sheets.

## Typical sheet set (adjust to the jurisdiction's submittal checklist)
A0.0 cover · A1.0 site · A2.x floor plans · A3.0 roof · A4.0 elevations · A5.0 sections ·
A6.0 details · S1.0 foundation · S2.0 framing · E1.0 electrical · P1.0 plumbing · M1.0 mechanical
(+ energy compliance forms where required).

## Project facts
See `project.json`. Fields still marked `(TBD)` are unknown — ask the owner, don't invent them.
Never guess structural sizes (footings, beams, headers, shear walls): mark them
"PER STRUCTURAL ENGINEER" until engineering is provided.

## Git
Commit sheet changes together with regenerated `output/` files so the PDFs in the repo match the code.
