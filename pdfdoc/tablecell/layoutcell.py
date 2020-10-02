#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
# This file is part of the legocad python module.
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# LayoutCell class

from reportlab.pdfgen import canvas

from toolbox import *
from pdfdoc import *

CONSTRAINT_TOKENS = [
    "left",
    "right",
    "top",
    "bottom",
    "above",
    "below",
    "rightof",
    "leftof",
    "centre",
    "center",
    "middleof",
    "resize",
    "between_horz",
    "between_vert",
    "between",
]
SINGLE_TOKENS = ["above", "below", "rightof", "leftof", "middleof"]
BETWEEN_TOKENS = ["between", "between_horz", "between_vert"]


def extract_labels(constraint):
    """ Extracts strings from constraint which are not tokens in CONSTRAINT_TOKENS or
    SINGLE_TOKENS.  These extracted strings are labels of other cells. """
    labels = []
    c = constraint.split()
    for e in c:
        if e not in CONSTRAINT_TOKENS:
            labels.append(e)
    return labels


def split_with_token(constraint, token):
    c = constraint.split()
    cu = []
    for e in c:
        if e.lower() == token.lower():
            cu.append(token.upper())
        else:
            cu.append(e)
    c = " ".join(cu)
    c = c.split(token.upper())
    return c


def parse_constraint(constraint):
    """ Parses a constraint into a dictionary which describes the source/from
    point (from_pt) and where it should be transformed to (dest_pt).  Optional
    labels describing which cell(s) the destination point is referring to are
    also extracted. """
    cdict = {"from_pt": None, "dest_pt": None, "dest_labels": []}
    c = constraint.lower()
    for token in SINGLE_TOKENS:
        if token in c:
            cdict["dest_pt"] = token
            cdict["dest_labels"] = extract_labels(constraint)
            return cdict
    for token in BETWEEN_TOKENS:
        if token in c.split():
            cb = split_with_token(constraint, "and")
            if len(cb) == 2:
                g1 = extract_labels(cb[0])
                g2 = extract_labels(cb[1])
                cdict[token] = {"group1": g1, "group2": g2}
                return cdict

    c = split_with_token(constraint, "to")
    if len(c) == 2:
        other = extract_labels(c[1])
        if len(other) > 0:
            cdict["from_pt"] = c[0]
            d = c[1]
            for e in other:
                d = d.replace(e, "")
            cdict["dest_pt"] = d
            cdict["dest_labels"] = other
        else:
            cdict["from_pt"] = c[0]
            cdict["dest_pt"] = c[1]
    else:
        cdict["from_pt"] = c[0]
        cdict["dest_pt"] = c[0]
    return cdict


def dummy_rect_from_parent_edge(parent_rect, edges):
    edges = edges.split("_")
    x, y = parent_rect.get_centre()
    valid = False
    for e in edges:
        if e == "left":
            x = parent_rect.left
            valid = True
        elif e == "right":
            x = parent_rect.right
            valid = True
        elif e == "top":
            y = parent_rect.top
            valid = True
        elif e == "bottom":
            y = parent_rect.bottom
            valid = True
    if valid:
        drect = Rect(0, 0)
        drect.move_to((x, y))
        return drect
    return None


class LayoutCell(TableVector):
    """ A LayoutCell is a sub-class of TableVector.  It contains one or more TableCells
    (with content as a ContentRect type).  LayoutCell is populated by constraints 
    describing a cell's relationship to the parent container (self) and/or other
    sibling TableCell items.  Each constraint is a string description of how one or
    more anchor points in the cell's rectangle should be placed relative to either
    the parent container rectangle or another cell's rectangle.
    Examples:
            "top left" - top left corner aligned to parent top left container rect
            "bottom right to centre" - bottom right corner aligned to parent's centre
            "below Cell2" - cell rectangle placed below Cell2's rectangle
            "above Cell1 Cell3" - cell rectangle placed above both Cell1 and Cell3
            "between Cell1 and Cell2 parent_right"
        In general constraints are in the form of:
            <my ref point> TO <parent ref point>
        or  <my ref point> TO <label ref point>
        or  below, above, rightof, leftof <[labels]>
    """

    def __init__(self, w, h, style=None):
        super().__init__(w, h, style)
        self.width_constraint = w
        self.height_constraint = h

    def __str__(self):
        s = []
        s.append("LayoutCell: %r" % (self))
        s.append("  Cell count: %d" % (len(self.cells)))
        s.append("  Rect: %s" % (str(self.rect)))
        w, h = self.get_content_size()
        s.append("  Content size: %.1f, %.1f" % (w, h))
        clipped = self.has_clipped_cells()
        overlapped = self.has_overlapped_cells()
        ratio = self.get_whitespace_ratio()
        s.append("  Clipped cells: %s Overlapped cells: %s" % (clipped, overlapped))
        s.append("  Whitespace ratio: %.1f%%" % (ratio * 100.0))
        s.append("  Overlay content: %r" % (self.overlay_content))
        s.append("  Show debug rects: %s" % (self.show_debug_rects))
        s.append(
            "  Width/height constraint: %.1f, %.1f"
            % (self.width_constraint, self.height_constraint)
        )
        s.append(
            "  Width/height total: %.1f, %.1f" % (self.total_width, self.total_height)
        )
        idx = 1
        for cell in self.iter_cells(only_visible=False):
            s.append(
                "  %d. Cell(%-12s) order=%-2d visible=%-5s type=%r"
                % (idx, cell.label, cell.order, cell.visible, cell.content)
            )
            if cell.visible:
                s.append(
                    "      rect: %s content size: (%.1f, %.1f)"
                    % (cell.content.rect, *cell.content.get_content_size())
                )
                s.append("      constraints: %s" % (cell.constraints))
            idx += 1
        return "\n".join(s)

    def layout_cells(self):
        w = self.fixed_rect.width if self.is_fixed_width else self.rect.width
        h = self.fixed_rect.height if self.is_fixed_height else self.rect.height
        self.rect.set_size_anchored(w, h, anchor_pt="top left")
        prect = self.style.get_inset_rect(self.rect)
        for cell in self.iter_cells():
            crect = self.get_cell_rect(cell.label)
            if cell.constraints is not None:
                for c in cell.constraints:
                    cd = parse_constraint(c)
                    if any([x in cd for x in BETWEEN_TOKENS]):
                        if "between" in cd:
                            bt = "between"
                        if "between_horz" in cd:
                            bt = "between_horz"
                        if "between_vert" in cd:
                            bt = "between_vert"
                        g1r = []
                        g2r = []
                        for x in cd[bt]["group1"]:
                            if self.is_cell_visible(x):
                                g1r.append(self.get_cell_rect(x))
                            else:
                                pr = dummy_rect_from_parent_edge(prect, x)
                                if pr is not None:
                                    g1r.append(pr)
                        for x in cd[bt]["group2"]:
                            if self.is_cell_visible(x):
                                g2r.append(self.get_cell_rect(x))
                            else:
                                pr = dummy_rect_from_parent_edge(prect, x)
                                if pr is not None:
                                    g2r.append(pr)
                        if len(g1r) > 0 and len(g2r) > 0:
                            g1_rect = Rect.bounding_rect_from_rects(g1r)
                            g2_rect = Rect.bounding_rect_from_rects(g2r)
                            if "between_vert" in cd or "between" in cd:
                                if g1_rect.bottom > g2_rect.top:
                                    mid_y = (
                                        g2_rect.top + (g1_rect.bottom - g2_rect.top) / 2
                                    )
                                else:
                                    mid_y = (
                                        g1_rect.top + (g2_rect.bottom - g1_rect.top) / 2
                                    )
                                crx, cry = crect.get_centre()
                                crect.move_to((crx, mid_y))
                            if "between_horz" in cd or "between" in cd:
                                if g1_rect.right < g2_rect.left:
                                    mid_x = (
                                        g1_rect.right
                                        + (g2_rect.left - g1_rect.right) / 2
                                    )
                                else:
                                    mid_x = (
                                        g2_rect.right
                                        + (g1_rect.left - g2_rect.right) / 2
                                    )
                                crx, cry = crect.get_centre()
                                crect.move_to((mid_x, cry))
                    elif len(cd["dest_labels"]) > 0:
                        others = []
                        for dest in cd["dest_labels"]:
                            if self.is_cell_visible(dest):
                                dest_rect = self.get_cell_rect(dest)
                                others.append(dest_rect)
                        other_rect = Rect.bounding_rect_from_rects(others)
                        if cd["from_pt"] is not None:
                            crect.anchor_with_constraint(
                                other_rect, cd["from_pt"] + " to " + cd["dest_pt"]
                            )
                        else:
                            crect.anchor_with_constraint(other_rect, cd["dest_pt"])
                    else:
                        if cd["from_pt"] is not None:
                            crect.anchor_with_constraint(
                                prect, cd["from_pt"] + " to " + cd["dest_pt"]
                            )
                        else:
                            crect.anchor_with_constraint(prect, cd["dest_pt"])
            else:
                # default to top left of parent container if no constraints are specified
                crect = self.get_cell_rect(cell.label)
                crect.anchor_with_constraint(prect, "top left to top left")
            self.set_cell_rect(cell.label, crect)

    def add_cell(self, label, content, order=None, constraints=None):
        if order is not None:
            cell = TableCell(label, content, order, 0, 0)
        else:
            cell = TableCell(label, content, len(self.cells), 0, 0)
        cell.constraints = constraints
        self.cells.append(cell)

    def get_content_size(self, with_padding=True):
        self.compute_cell_layout()
        r = self.get_cell_rects(as_is=True)
        rb = Rect.bounding_rect_from_rects(r)
        self.total_width = rb.width
        self.total_height = rb.height
        if with_padding:
            self.total_width += self.style.get_width_trim()
            self.total_height += self.style.get_height_trim()
        if self.is_fixed_width:
            self.total_width = self.fixed_rect.width
        if self.is_fixed_height:
            self.total_height = self.fixed_rect.height
        return self.total_width, self.total_height

    def compute_cell_layout(self):
        self.compute_cell_order()
        rpt = self.rect.get_top_left()
        rects = []
        for cell in self.iter_cells():
            cw, ch = cell.content.get_content_size()
            r = Rect(cw, ch)
            self.set_cell_rect(cell.label, r)
        self.layout_cells()
        all_rects = self.get_cell_rects(as_is=True)
        bounds = Rect.bounding_rect_from_rects(self.get_cell_rects(as_is=True))
        self.total_width = bounds.width + self.style.get_width_trim()
        self.total_height = bounds.height + self.style.get_height_trim()
        self.rect.set_size(self.total_width, self.total_height)
        self.rect.move_top_left_to(rpt)
        self.assign_cell_overlay_content_rects()

    def draw_in_canvas(self, canvas):
        self.draw_cells_in_canvas(canvas)

    def draw_cells_in_canvas(self, canvas):
        self.compute_cell_layout()
        self.draw_background(canvas)
        for cell in self.iter_cells():
            cell.content.draw_in_canvas(canvas)
        self.draw_border_lines(canvas)
        if self.overlay_content is not None:
            self.overlay_content.draw_in_canvas(canvas)
        if self.show_debug_rects:
            self.draw_debug_rect(canvas, self.rect)
            inset_rect = self.style.get_inset_rect(self.rect)
            self.draw_debug_rect(canvas, inset_rect, (0, 0, 1))