"""Text-block helpers for notes/data sheets (paper inches)."""
from ezdxf.enums import TextEntityAlignment

from plans.lib import mtext, rect, text

H = 0.14          # body text height
LS = 0.25         # line spacing


def header(msp, x, y, w, title):
    """Section header bar; returns y of first body line."""
    rect(msp, x, y - 0.32, x + w, y, "A-ANNO")
    text(msp, title, (x + w / 2, y - 0.16), h=0.16, layer="A-ANNO-TITL", align=TextEntityAlignment.MIDDLE_CENTER)
    return y - 0.55


def rows(msp, x, y, items, col2, w=None):
    """Two-column label/value rows; returns next y."""
    for k, v in items:
        text(msp, k, (x + 0.1, y), h=H)
        if w:
            mtext(msp, v, (x + col2, y + H), h=H, width=w)
            y -= LS * max(1, (len(v) * H * 0.9) // w + 1)
        else:
            text(msp, v, (x + col2, y), h=H)
            y -= LS
    return y


def para(msp, x, y, lines, w):
    """Numbered/plain lines as wrapped mtext; returns approx next y."""
    for ln in lines:
        mtext(msp, ln, (x + 0.1, y + H), h=H, width=w - 0.2)
        n = max(1, int(len(ln) * H * 0.82 / (w - 0.2)) + 1)
        y -= LS * n + 0.04
    return y
