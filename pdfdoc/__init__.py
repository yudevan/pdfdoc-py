"""pdfdoc - Python utility library for compositing PDF documents with reportlab."""

import os

# fmt: off
__project__ = 'pdfdoc'
__version__ = '0.9.0'
# fmt: on

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

DEF_FONT_NAME = "DroidSans"
DEF_FONT_SIZE = 15
AUTO_SIZE = 0
CONTENT_SIZE = -1

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from .helpers import (
    GetImageMetrics,
    GetStringMetrics,
    GetStringAscDes,
    GetImageMetrics,
    TrimStringToFit,
    SplitStringToFit,
    TrimStringWithFunction,
    rl_colour,
    rl_colour_trans,
)
from .fonthelpers import (
    register_font_family,
    register_font,
    fasymbol,
    hazsymbol,
    set_icon,
    list_fonts,
    find_font,
    create_specimen_pdf,
)
from .style.docstyle import DocStyle, DocStyleSheet, roman_number
from .style.pagestyles import *
from .style.labelstyles import *
from .contentrect.contentrect import ContentRect
from .contentrect.textrect import TextRect
from .contentrect.imgrect import ImageRect
from .contentrect.patternrect import PatternRect
from .contentrect.alignmentrect import AlignmentRect
from .tablecell.tablecell import TableCell
from .tablecell.tablevector import TableVector
from .tablecell.tablegrid import TableGrid
from .tablecell.layoutcell import LayoutCell
from .tablecell.tablerow import TableRow
from .tablecell.tablecolumn import TableColumn
from .document.document import Document
from .document.doccallbacks import *
from .labeldoc.labeldoc import LabelDoc
from .labeldoc.genericlabel import GenericLabel
from .labeldoc.safetylabel import SafetyLabel
from .labeldoc.mechlabel import MechanicalLabel
from .labeldoc.eleclabel import ElectronicLabel
from .graphics.arrowhead import ArrowHead

font_dict = {
    "DroidSans": "DroidSans.ttf",
    "DroidSans-Bold": "DroidSans-Bold.ttf",
    "DIN-Medium": "DIN-Medium.ttf",
    "DIN-Regular": "DIN-Regular.ttf",
    "DIN-Bold": "DIN-Bold.ttf",
    "IKEA-Sans-Regular": "IKEA-Sans-Regular.ttf",
    "IKEA-Sans-Heavy": "IKEA-Sans-Heavy.ttf",
    "British-Rail-Light": "britrln_.ttf",
    "British-Rail-Dark": "britrdn_.ttf",
    "FontAwesome": "fontawesome-webfont.ttf",
    "Hazard": "haw_____.ttf",
    "Zapf Dingbats": "ZapfDingbats.ttf",
}

for k, v in font_dict.items():
    try:
        pdfmetrics.registerFont(TTFont(k, v))
    except:
        print("Warning: could not load and register font %s with filename %s" % (k, v))
