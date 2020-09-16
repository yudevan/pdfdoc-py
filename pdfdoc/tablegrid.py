#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
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
# TableGrid class

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import Color

from fxgeometry import Rect, Point
from .docstyle import DocStyle
from .pdfdoc import rl_colour, rl_colour_trans
from .tablecell import TableCell, TableVector


class TableGrid(TableVector):
    """ A TableGrid is a sub-class of TableVector.  It can contain multiple rows and columns of 
    content cells (TableCell objects with a type of ContentRect as actual content).  TableGrid
    is filled either row-wise or column-wise based on the cell order.  When filling row-wise,
    a row is automatically created when the previous row's content size has exceeded
    width_constraint.  Similarly, a new column is created when height_constraint to exceeded."""

    def __init__(self, w, h, style=None):
        super().__init__(w, h, style)
        self.fill_dir = "row-wise"
        self.width_constraint = w
        self.height_constraint = h
        self.total_width = 0
        self.total_height = 0
        self.auto_adjust = True

    def add_cell(self, label, content, order=None):
        if order is not None:
            cell = TableCell(label, content, order, 0, 0)
        else:
            cell = TableCell(label, content, len(self.cells), 0, 0)
        self.cells.append(cell)

    def set_cell_order(self, label, order):
        self.set_cell_order(label, order)

    def set_cell_content(self, label, content):
        cell = self.get_cell(label)
        if cell is not None:
            cell.content = content

    def get_content_size(self, with_padding=True):
        self.compute_cell_sizes()
        r = self.get_cell_rects(as_is=True)
        if len(r) > 0:
            rb = Rect.bounding_rect_from_rects(r)
        else:
            rb = Rect(0, 0)
        self.total_width = rb.width
        self.total_height = rb.height
        if with_padding:
            self.total_width += self.style.get_width_trim()
            self.total_height += self.style.get_height_trim()
        return self.total_width, self.total_height

    def compute_cell_sizes(self):
        self.compute_cell_order()
        rpt = self.rect.get_top_left()
        r = Rect(width=self.width_constraint, height=self.height_constraint)
        cell_rect = self.style.get_inset_rect(r)
        inrect = self.style.get_inset_rect(self.rect)
        cell_rect.move_top_left_to(inrect.get_top_left())
        rects = []
        for cell in self.iter_cells():
            cw, ch = cell.content.get_content_size()
            r = Rect(cw, ch)
            rects.append(r)
        row_wise = True if self.fill_dir == "row-wise" else False
        vert_align = self.style.get_attr("vert-align")
        horz_align = self.style.get_attr("horz-align")
        new_rects = Rect.layout_rects(
            rects,
            cell_rect,
            row_wise=row_wise,
            vert_align=vert_align,
            horz_align=horz_align,
            auto_adjust=self.auto_adjust,
        )
        idx = 0
        for cell in self.iter_cells():
            cell.content.rect.set_size(
                new_rects[idx].width, new_rects[idx].height
            )
            cell.content.rect.move_top_left_to(
                (new_rects[idx].left, new_rects[idx].top)
            )
            idx += 1
        bounds = Rect.bounding_rect_from_rects(new_rects)
        self.total_width = bounds.width + self.style.get_width_trim()
        self.total_height = bounds.height + self.style.get_height_trim()
        self.rect.set_size(self.total_width, self.total_height)
        self.rect.move_top_left_to(rpt)

        self.assign_cell_overlay_content_rects()

    def draw_in_canvas(self, canvas):
        self.draw_cells_in_canvas(canvas)

    def draw_cells_in_canvas(self, canvas):
        self.compute_cell_sizes()
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
