# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from pdfdoc import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

_test_dict = {
    "length": 0.4 * inch,
    "width": 0.1 * inch,
    "border-colour": (0.8, 0.8, 1.0),
    "line-colour": (0, 0, 0),
    "border-width": 0.01 * inch,
    "border-outline": True,
    "arrow-style": "taper",
}


def test_arrowhead():
    a1 = ArrowHead(style=_test_dict)
    c = canvas.Canvas(
        "./testfiles/test_arrowhead.pdf", pagesize=(8.5 * inch, 11.0 * inch)
    )
    p1 = (4 * inch, 9 * inch)
    p2 = (6 * inch, 6 * inch)
    p3 = (4 * inch, 3 * inch)
    p4 = (2 * inch, 6 * inch)
    a1.draw_in_canvas(c, p1, dir=90)
    a1.draw_in_canvas(c, p2, dir=0)
    a1.draw_in_canvas(c, p3, dir=-90)
    a1.draw_in_canvas(c, p4, dir=180)

    p1 = (5 * inch, 9 * inch)
    p2 = (7 * inch, 6 * inch)
    p3 = (5 * inch, 3 * inch)
    p4 = (3 * inch, 6 * inch)
    a1.style["arrow-style"] = "flat"
    a1.style["border-outline"] = False
    a1.draw_in_canvas(c, p1, dir=90)
    a1.draw_in_canvas(c, p2, dir=0)
    a1.draw_in_canvas(c, p3, dir=-90)
    a1.draw_in_canvas(c, p4, dir=180)

    c.showPage()
    c.save()
