#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the undergraduate thesis proposal (.docx) from a Markdown source.

Usage:
    python build_proposal_docx.py [src.md] [out.docx]

Defaults:
    src = thesis/proposal.md
    out = deliverables/毕业设计开题报告-v2-20261027.docx

Supported Markdown conventions
------------------------------
<!-- cover --> ... <!-- /cover -->   cover page; one paragraph per line, centered,
                                    first line 22pt 黑体 bold, other lines 14pt 宋体,
                                    block sits in the upper-middle of the page,
                                    page break right after the closing marker
<!-- pagebreak -->                  page break (implemented as pageBreakBefore on the
                                    next block, so no stray empty paragraph appears)
# 标题                              document title, centered 18pt 黑体 bold
## 标题 / ### 标题                  level-1 / level-2 heading, mapped onto the built-in
                                    Word styles "Heading 1" / "Heading 2" (pStyle +
                                    outlineLvl), so the navigation pane and an
                                    auto-generated TOC both work
![图 6-1 说明](figures/x.png)       centered picture (14.0 cm wide, no border) followed
                                    by a centered caption
表 7-1 说明  [+ optional blank line]  table caption (centered 10.5pt, keep_with_next);
| ... | 表格块                       table body, header row repeated across pages,
                                    no row split across pages, no empty paragraph after
**粗体**                            inline bold
[12] [12,35] [23-27]                inline citation markers rendered as superscript
                                    (skipped inside the reference list)
## 主要参考文献 + [1] ...            reference list: hanging indent, 10.5pt, single line
                                    spacing

Layout: A4, top/bottom 2.54 cm, left 3.0 cm, right 2.6 cm (text width 15.4 cm).
Normal style: 宋体 12pt (小四), 1.5 line spacing, first-line indent 2 characters,
justified, no space before/after.
"""
import datetime
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.font import Font

# --------------------------------------------------------------------------- #
# constants
# --------------------------------------------------------------------------- #
BODY_FONT = "宋体"
HEAD_FONT = "黑体"
BODY_SIZE = Pt(12)          # 小四
TABLE_SIZE = Pt(10.5)       # 五号
REF_SIZE = Pt(10.5)         # 五号
HEADER_SIZE = Pt(9)         # 小五
BLACK = RGBColor(0x00, 0x00, 0x00)

PAGE_WIDTH = Cm(21.0)
PAGE_HEIGHT = Cm(29.7)
MARGIN_TOP = Cm(2.54)
MARGIN_BOTTOM = Cm(2.54)
MARGIN_LEFT = Cm(3.0)
MARGIN_RIGHT = Cm(2.6)
TEXT_WIDTH_CM = 15.4        # 21.0 - 3.0 - 2.6
FIG_WIDTH_CM = 14.0         # deliberately < text width so the figure does not touch
                            # the margins
COVER_TOP_SPACE = Cm(3.5)   # pushes the cover block into the upper-middle area

HEADER_TEXT = "本科毕业设计（论文）开题报告"

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SRC = ROOT / "thesis" / "proposal.md"
DEFAULT_OUT = ROOT / "deliverables" / "毕业设计开题报告-v2-20261027.docx"

CM_TO_TWIPS = 1440.0 / 2.54

# --------------------------------------------------------------------------- #
# regexes
# --------------------------------------------------------------------------- #
RE_COVER_OPEN = re.compile(r"^<!--\s*cover\s*-->$")
RE_COVER_CLOSE = re.compile(r"^<!--\s*/\s*cover\s*-->$")
RE_PAGEBREAK = re.compile(r"^<!--\s*pagebreak\s*-->$")
RE_FIGURE = re.compile(r"^!\[(.*?)\]\((.+?)\)$")
RE_TABLE_CAPTION = re.compile(r"^表\s*\d+(?:\s*[-－.．]\s*\d+)?")
RE_REF_LINE = re.compile(r"^\[\d+\]")
# either **bold** or a citation marker; group 1 = bold text, group 2 = citation
RE_INLINE = re.compile(r"\*\*(.+?)\*\*|(\[\d+(?:\s*[,，\-–－]\s*\d+)*\])")

# --------------------------------------------------------------------------- #
# OOXML child ordering (kept in schema order so Word never complains)
# --------------------------------------------------------------------------- #
_PPR_ORDER = tuple(qn(t) for t in (
    "w:pStyle", "w:keepNext", "w:keepLines", "w:pageBreakBefore", "w:framePr",
    "w:widowControl", "w:numPr", "w:suppressLineNumbers", "w:pBdr", "w:shd",
    "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap",
    "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN",
    "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
    "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
    "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
    "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange",
))
_RPR_ORDER = tuple(qn(t) for t in (
    "w:rStyle", "w:rFonts", "w:b", "w:bCs", "w:i", "w:iCs", "w:caps",
    "w:smallCaps", "w:strike", "w:dstrike", "w:outline", "w:shadow", "w:emboss",
    "w:imprint", "w:noProof", "w:snapToGrid", "w:vanish", "w:webHidden",
    "w:color", "w:spacing", "w:w", "w:kern", "w:position", "w:sz", "w:szCs",
    "w:highlight", "w:u", "w:effect", "w:bdr", "w:shd", "w:fitText",
    "w:vertAlign", "w:rtl", "w:cs", "w:em", "w:lang", "w:eastAsianLayout",
    "w:specVanish", "w:oMath",
))
_STYLE_ORDER = tuple(qn(t) for t in (
    "w:name", "w:aliases", "w:basedOn", "w:next", "w:link", "w:autoRedefine",
    "w:hidden", "w:uiPriority", "w:semiHidden", "w:unhideWhenUsed", "w:qFormat",
    "w:locked", "w:personal", "w:personalCompose", "w:personalReply", "w:rsid",
    "w:pPr", "w:rPr", "w:tblPr", "w:trPr", "w:tcPr", "w:tblStylePr",
))
_TBLPR_ORDER = tuple(qn(t) for t in (
    "w:tblStyle", "w:tblpPr", "w:tblOverlap", "w:bidiVisual",
    "w:tblStyleRowBandSize", "w:tblStyleColBandSize", "w:tblW", "w:jc",
    "w:tblCellSpacing", "w:tblInd", "w:tblBorders", "w:shd", "w:tblLayout",
    "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription",
    "w:tblPrChange",
))
_TRPR_ORDER = tuple(qn(t) for t in (
    "w:cnfStyle", "w:divId", "w:gridBefore", "w:gridAfter", "w:wBefore",
    "w:wAfter", "w:cantSplit", "w:trHeight", "w:tblHeader", "w:tblCellSpacing",
    "w:jc", "w:hidden", "w:ins", "w:del", "w:trPrChange",
))
_TCPR_ORDER = tuple(qn(t) for t in (
    "w:cnfStyle", "w:tcW", "w:gridSpan", "w:hMerge", "w:vMerge", "w:tcBorders",
    "w:shd", "w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText",
    "w:vAlign", "w:hideMark", "w:headers", "w:cellIns", "w:cellDel",
    "w:cellMerge", "w:tcPrChange",
))


def insert_ordered(parent, child, order):
    """Insert *child* into *parent* at its schema-correct position."""
    tag = child.tag
    idx = order.index(tag) if tag in order else len(order)
    for existing in list(parent):
        if existing.tag in order and order.index(existing.tag) > idx:
            existing.addprevious(child)
            return child
    parent.append(child)
    return child


def ensure_child(parent, tag, order):
    """Return ``parent/tag``, creating it at the schema-correct position."""
    found = parent.find(qn(tag))
    if found is not None:
        return found
    return insert_ordered(parent, OxmlElement(tag), order)


# --------------------------------------------------------------------------- #
# run / style formatting
# --------------------------------------------------------------------------- #
def strip_theme_attrs(rfonts):
    """Remove asciiTheme/... so explicit font names actually win in Word."""
    for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        key = qn("w:" + attr)
        if key in rfonts.attrib:
            del rfonts.attrib[key]


def set_run_font(run, font=BODY_FONT, size=BODY_SIZE, bold=False, color=None,
                 superscript=False):
    """Format one run, including the eastAsia font (required for CJK glyphs)."""
    run.font.name = font
    run.font.size = size
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    if superscript:
        run.font.superscript = True
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = ensure_child(rpr, "w:rFonts", _RPR_ORDER)
    strip_theme_attrs(rfonts)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:eastAsia"), font)
    rfonts.set(qn("w:cs"), font)
    return run


def add_runs(paragraph, text, font=BODY_FONT, size=BODY_SIZE, base_bold=False,
             citations=True):
    """Render one text fragment: **bold** segments and [n] superscript citations."""
    if not text:
        return paragraph
    pos = 0
    for match in RE_INLINE.finditer(text):
        if match.start() > pos:
            set_run_font(paragraph.add_run(text[pos:match.start()]), font, size,
                         base_bold)
        if match.group(1) is not None:                    # **bold**
            set_run_font(paragraph.add_run(match.group(1)), font, size, True)
        else:                                             # [12] citation marker
            set_run_font(paragraph.add_run(match.group(0)), font, size,
                         base_bold, superscript=citations)
        pos = match.end()
    if pos < len(text):
        set_run_font(paragraph.add_run(text[pos:]), font, size, base_bold)
    return paragraph


def set_style_font(style, font, size, bold, color=None):
    """Override a built-in style's font; kills the theme blue of Heading styles."""
    # Font() wraps the style element itself (it owns get_or_add_rPr)
    f = Font(style.element)
    f.name = font
    f.size = size
    f.bold = bold
    f.italic = False
    if color is not None:
        f.color.rgb = color
    rpr = style.element.get_or_add_rPr()
    rfonts = ensure_child(rpr, "w:rFonts", _RPR_ORDER)
    strip_theme_attrs(rfonts)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:eastAsia"), font)
    rfonts.set(qn("w:cs"), font)
    # keep the complex-script size in sync (the template leaves stale values)
    ensure_child(rpr, "w:szCs", _RPR_ORDER).set(qn("w:val"),
                                                str(int(round(size.pt * 2))))
    color_el = rpr.find(qn("w:color"))
    if color_el is not None:                     # belt and braces: no theme colour
        for attr in ("themeColor", "themeTint", "themeShade"):
            key = qn("w:" + attr)
            if key in color_el.attrib:
                del color_el.attrib[key]


def set_outline_level(paragraph_or_style_element, level):
    """Write ``w:outlineLvl`` (0-based) so the heading shows in the nav pane."""
    ppr = ensure_child(paragraph_or_style_element, "w:pPr", _PPR_ORDER)
    el = ensure_child(ppr, "w:outlineLvl", _PPR_ORDER)
    el.set(qn("w:val"), str(level))


def set_first_line_chars(paragraph_format, chars=2, size_pt=BODY_SIZE.pt):
    """First-line indent expressed in characters (w:firstLineChars) + twips."""
    ppr = paragraph_format.element.get_or_add_pPr()
    ind = ensure_child(ppr, "w:ind", _PPR_ORDER)
    ind.set(qn("w:firstLineChars"), str(int(chars * 100)))
    ind.set(qn("w:firstLine"), str(int(round(size_pt * chars * 20))))
    for attr in ("w:left", "w:start", "w:leftChars", "w:startChars",
                 "w:hanging", "w:hangingChars"):
        key = qn(attr)
        if key in ind.attrib:
            del ind.attrib[key]


def zero_indent(paragraph_format):
    """Cancel the inherited Normal first-line indent (headings, captions, cells)."""
    ppr = paragraph_format.element.get_or_add_pPr()
    ind = ensure_child(ppr, "w:ind", _PPR_ORDER)
    for attr in ("w:firstLine", "w:firstLineChars", "w:left", "w:start",
                 "w:leftChars", "w:startChars"):
        key = qn(attr)
        if key in ind.attrib:
            del ind.attrib[key]
    ind.set(qn("w:firstLine"), "0")
    ind.set(qn("w:left"), "0")


def set_paragraph_bottom_border(paragraph, sz=6, color="000000"):
    """Single rule under the header text."""
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = ensure_child(ppr, "w:pBdr", _PPR_ORDER)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)


# --------------------------------------------------------------------------- #
# table helpers
# --------------------------------------------------------------------------- #
def cm_to_twips(value_cm):
    return str(int(round(value_cm * CM_TO_TWIPS)))


def pick_col_widths(header):
    """Column widths (cm) from the header row; every rule sums to 15.4 cm."""
    n = len(header)
    flat = "".join(header)
    if n == 2:
        return [3.4, 12.0]
    if n == 3:
        if any(("签字" in h or "签名" in h or "日期" in h) for h in header[1:]):
            return [3.2, 8.8, 3.4]        # 栏目 / 内容 / 签字：给签字列留白
        return [3.2, 5.6, 6.6]
    if n == 4:
        if "阶段" in header[0]:
            return [1.4, 3.4, 7.2, 3.4]   # 阶段 / 时间 / 主要工作 / 阶段成果
        if any(k in flat for k in ("编号", "序号", "位置", "问题", "建议")):
            return [2.2, 3.0, 6.6, 3.6]   # 编号 / 位置 / 问题 / 建议
        return [3.0, 4.4, 4.6, 3.4]
    if n == 5:
        if "编号" in header[0]:
            # 编号 / 指标 / 定义与口径 / 载体与来源 / 报告方式：编号列须容下 M10/M11，
            # 载体列须容下 metric_provenance.py 这类不断词的长标识
            return [2.0, 2.2, 3.9, 4.4, 2.9]
        return [1.4, 2.4, 5.6, 3.0, 3.0]
    width = round(TEXT_WIDTH_CM / n, 2)
    widths = [width] * n
    widths[-1] = round(TEXT_WIDTH_CM - width * (n - 1), 2)
    return widths


def set_col_widths(table, widths_cm):
    """Fixed layout: tblW + tblGrid/gridCol + every cell's tcW."""
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = ensure_child(tbl_pr, "w:tblW", _TBLPR_ORDER)
    tbl_w.set(qn("w:type"), "dxa")
    tbl_w.set(qn("w:w"), cm_to_twips(sum(widths_cm)))
    grid = table._tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for grid_col, width in zip(grid.findall(qn("w:gridCol")), widths_cm):
            grid_col.set(qn("w:w"), cm_to_twips(width))
    for row in table.rows:
        for idx, width in enumerate(widths_cm):
            if idx < len(row.cells):
                row.cells[idx].width = Cm(width)


def set_table_cell_margins(table, side_cm=0.08, vertical_cm=0.0):
    """Shrink the default 0.19 cm cell margins so narrow columns still fit their
    header text (a 1.2 cm 阶段 column must hold two 10.5pt characters)."""
    tbl_pr = table._tbl.tblPr
    margins = ensure_child(tbl_pr, "w:tblCellMar", _TBLPR_ORDER)
    for edge, value in (("top", vertical_cm), ("left", side_cm),
                        ("bottom", vertical_cm), ("right", side_cm)):
        el = margins.find(qn("w:" + edge))
        if el is None:
            el = OxmlElement("w:" + edge)
            margins.append(el)
        el.set(qn("w:w"), cm_to_twips(value))
        el.set(qn("w:type"), "dxa")


def shade_cell(cell, fill="F2F2F2"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = ensure_child(tc_pr, "w:shd", _TCPR_ORDER)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)


def set_cell_valign(cell, value="center"):
    tc_pr = cell._tc.get_or_add_tcPr()
    valign = ensure_child(tc_pr, "w:vAlign", _TCPR_ORDER)
    valign.set(qn("w:val"), value)


def mark_header_row(row):
    """<w:tblHeader/>: repeat the header row on every page the table spans."""
    tr_pr = row._tr.get_or_add_trPr()
    el = ensure_child(tr_pr, "w:tblHeader", _TRPR_ORDER)
    el.set(qn("w:val"), "true")


def mark_row_cant_split(row):
    """<w:cantSplit/>: never break this row across two pages."""
    tr_pr = row._tr.get_or_add_trPr()
    el = ensure_child(tr_pr, "w:cantSplit", _TRPR_ORDER)
    el.set(qn("w:val"), "true")


# --------------------------------------------------------------------------- #
# builder
# --------------------------------------------------------------------------- #
class ProposalBuilder(object):
    """Markdown -> docx converter for the proposal."""

    def __init__(self, src, out):
        self.src = Path(src)
        self.out = Path(out)
        self.doc = Document()
        self.in_refs = False
        self._pending_break = False
        self._setup_page()
        self._setup_styles()
        self._setup_header_footer()
        self._setup_properties()

    # -- page / styles ----------------------------------------------------- #
    def _setup_properties(self):
        """Document properties (metadata only; python-docx cannot paginate)."""
        props = self.doc.core_properties
        props.title = "本科毕业设计（论文）开题报告"
        props.subject = "面向代码智能体的开发任务上下文追踪与代码变更溯源系统设计与实现"
        props.keywords = "代码智能体；开发任务；上下文追踪；代码变更溯源"
        props.comments = "由 scripts/build_proposal_docx.py 从 thesis/proposal.md 生成"
        props.author = "待填写"
        props.last_modified_by = "待填写"
        now = datetime.datetime.now().replace(microsecond=0)
        props.created = now
        props.modified = now
        props.revision = 1

    def _setup_page(self):
        sec = self.doc.sections[0]
        sec.page_width = PAGE_WIDTH
        sec.page_height = PAGE_HEIGHT
        sec.top_margin = MARGIN_TOP
        sec.bottom_margin = MARGIN_BOTTOM
        sec.left_margin = MARGIN_LEFT
        sec.right_margin = MARGIN_RIGHT
        sec.header_distance = Cm(1.5)
        sec.footer_distance = Cm(1.75)

    def _setup_styles(self):
        # Normal: 宋体 12pt, 1.5 倍行距, 首行缩进 2 字符, 两端对齐, 段前段后 0
        normal = self.doc.styles["Normal"]
        set_style_font(normal, BODY_FONT, BODY_SIZE, bold=False)
        pf = normal.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        set_first_line_chars(pf, 2, BODY_SIZE.pt)

        # Heading 1 / Heading 2: built-in styles, black 黑体, outlineLvl set
        self._setup_heading("Heading 1", level=1, size=Pt(14),
                            before=Pt(14), after=Pt(6))
        self._setup_heading("Heading 2", level=2, size=Pt(12),
                            before=Pt(10), after=Pt(4))

    def _setup_heading(self, style_name, level, size, before, after):
        style = self.doc.styles[style_name]
        # built-in Heading styles are blue by default -> force black + 黑体
        set_style_font(style, HEAD_FONT, size, bold=True, color=BLACK)
        pf = style.paragraph_format
        pf.space_before = before
        pf.space_after = after
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.keep_with_next = True
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        zero_indent(pf)
        set_outline_level(style.element, level - 1)

    def _setup_header_footer(self):
        sec = self.doc.sections[0]
        # 封面页不显示页眉与页码
        sec.different_first_page_header_footer = True

        # 页眉：宋体 9pt 居中 + 下边框单线
        header = sec.header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        for run in list(hp.runs):
            run._element.getparent().remove(run._element)
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hp.paragraph_format.space_before = Pt(0)
        hp.paragraph_format.space_after = Pt(0)
        hp.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        zero_indent(hp.paragraph_format)
        set_run_font(hp.add_run(HEADER_TEXT), BODY_FONT, HEADER_SIZE)
        set_paragraph_bottom_border(hp)

        # 页脚：PAGE 域，五段齐全（begin / instrText / separate / 结果 / end）
        footer = sec.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        for run in list(fp.runs):
            run._element.getparent().remove(run._element)
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.paragraph_format.space_before = Pt(0)
        fp.paragraph_format.space_after = Pt(0)
        zero_indent(fp.paragraph_format)
        self._add_page_field(fp, TABLE_SIZE)

    @staticmethod
    def _add_page_field(paragraph, size):
        def fld_char(kind):
            run = paragraph.add_run()
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
            run._r.append(el)
            return run

        begin = fld_char("begin")                       # 1. begin
        instr_run = paragraph.add_run()                 # 2. instrText PAGE
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = " PAGE "
        instr_run._r.append(instr)
        separate = fld_char("separate")                 # 3. separate
        result = paragraph.add_run("1")                 # 4. cached result text
        end = fld_char("end")                           # 5. end
        for run in (begin, instr_run, separate, result, end):
            set_run_font(run, BODY_FONT, size)

    # -- block primitives -------------------------------------------------- #
    def _apply_pending_break(self, paragraph):
        if self._pending_break:
            paragraph.paragraph_format.page_break_before = True
            self._pending_break = False

    def _new_paragraph(self, style=None):
        p = self.doc.add_paragraph(style=style) if style else self.doc.add_paragraph()
        self._apply_pending_break(p)
        return p

    def _flush_pending_break_before_table(self):
        """A table cannot carry pageBreakBefore: use a 1pt filler paragraph."""
        if not self._pending_break:
            return
        p = self._new_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing = Pt(1)
        zero_indent(pf)
        set_run_font(p.add_run(""), size=Pt(1))

    def add_body(self, text):
        p = self._new_paragraph()
        pf = p.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        set_first_line_chars(pf, 2, BODY_SIZE.pt)
        add_runs(p, text)
        return p

    def add_title(self, text):
        p = self._new_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = p.paragraph_format
        pf.space_before = Pt(6)
        pf.space_after = Pt(16)
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.keep_with_next = True
        zero_indent(pf)
        add_runs(p, text, font=HEAD_FONT, size=Pt(18), base_bold=True,
                 citations=False)
        return p

    def add_heading(self, text, level):
        style_name = {1: "Heading 1", 2: "Heading 2", 3: "Heading 3"}.get(
            level, "Heading 2"
        )
        p = self._new_paragraph(style=style_name)
        pf = p.paragraph_format
        pf.space_before = Pt(14 if level == 1 else 10)
        pf.space_after = Pt(6 if level == 1 else 4)
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.keep_with_next = True
        zero_indent(pf)
        set_outline_level(p._p, level - 1)
        add_runs(p, text, font=HEAD_FONT, size=Pt(14 if level == 1 else 12),
                 base_bold=True, citations=False)
        return p

    def add_cover(self, lines):
        first = True
        for raw in lines:
            text = raw.strip()
            p = self._new_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = p.paragraph_format
            pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
            zero_indent(pf)
            if not text:                       # intentional spacer line
                pf.space_before = Pt(0)
                pf.space_after = Pt(0)
                set_run_font(p.add_run(""), size=Pt(10))
                continue
            if first:
                pf.space_before = COVER_TOP_SPACE
                pf.space_after = Pt(24)
                add_runs(p, text, font=HEAD_FONT, size=Pt(22), base_bold=True,
                         citations=False)
                first = False
            else:
                pf.space_before = Pt(0)
                pf.space_after = Pt(6)
                add_runs(p, text, font=BODY_FONT, size=Pt(14), citations=False)

    def add_figure(self, caption, rel_path):
        image = self._resolve_image(rel_path)
        if image is None:
            self.add_body("[图片缺失：%s]" % rel_path)
            return None
        self.doc.add_picture(str(image), width=Cm(FIG_WIDTH_CM))
        pic_p = self.doc.paragraphs[-1]
        pf = pic_p.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.space_before = Pt(6)
        pf.space_after = Pt(0)
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.keep_with_next = True
        zero_indent(pf)
        self._apply_pending_break(pic_p)

        cap = self._new_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cpf = cap.paragraph_format
        cpf.space_before = Pt(3)
        cpf.space_after = Pt(10)
        cpf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        zero_indent(cpf)
        add_runs(cap, caption, size=TABLE_SIZE, citations=False)
        return cap

    def add_table_caption(self, text):
        p = self._new_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = p.paragraph_format
        pf.space_before = Pt(8)
        pf.space_after = Pt(3)
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.keep_with_next = True
        zero_indent(pf)
        add_runs(p, text, size=TABLE_SIZE, citations=False)
        return p

    def add_reference(self, text):
        p = self._new_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = Pt(13)
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.left_indent = Cm(0.85)
        pf.first_line_indent = Cm(-0.85)      # hanging indent
        add_runs(p, text, size=REF_SIZE, citations=False)
        return p

    def add_table(self, rows):
        self._flush_pending_break_before_table()
        header = rows[0]
        ncols = len(header)
        body = [(row + [""] * ncols)[:ncols] for row in rows[1:]]
        table = self.doc.add_table(rows=1 + len(body), cols=ncols)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_col_widths(table, pick_col_widths(header))
        set_table_cell_margins(table)

        header_row = table.rows[0]
        for j, text in enumerate(header):
            cell = header_row.cells[j]
            shade_cell(cell)
            set_cell_valign(cell)
            p = cell.paragraphs[0]
            self._prepare_cell_paragraph(p, center=True)
            add_runs(p, text, font=HEAD_FONT, size=TABLE_SIZE, base_bold=True)
        mark_header_row(header_row)

        col0_center = False
        if ncols >= 3 and body:
            col0_center = max(len(row[0]) for row in body) <= 10
        for i, row in enumerate(body, start=1):
            for j in range(ncols):
                cell = table.rows[i].cells[j]
                set_cell_valign(cell)
                p = cell.paragraphs[0]
                self._prepare_cell_paragraph(p, center=(j == 0 and col0_center))
                add_runs(p, row[j], size=TABLE_SIZE)

        for row in table.rows:                 # no row may be split by a page break
            mark_row_cant_split(row)

        # 签字表：给手写签名留出行高
        if header and ("签字" in header[-1] or "签名" in header[-1]):
            for row in table.rows[1:]:
                row.height = Cm(2.2)
        return table

    @staticmethod
    def _prepare_cell_paragraph(paragraph, center=False):
        pf = paragraph.paragraph_format
        pf.space_before = Pt(2)
        pf.space_after = Pt(2)
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.alignment = (WD_ALIGN_PARAGRAPH.CENTER if center
                        else WD_ALIGN_PARAGRAPH.LEFT)
        zero_indent(pf)

    # -- parsing helpers --------------------------------------------------- #
    def _resolve_image(self, rel_path):
        candidates = [
            (self.src.parent / rel_path).resolve(),
            (ROOT / rel_path).resolve(),
            Path(rel_path),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def _next_nonblank(lines, start):
        j = start
        while j < len(lines) and not lines[j].strip():
            j += 1
        return j

    @staticmethod
    def _collect_cover(lines, i):
        """*i* points at <!-- cover -->; return (cover lines, index after marker)."""
        cover = []
        i += 1
        while i < len(lines):
            if RE_COVER_CLOSE.match(lines[i].strip()):
                return cover, i + 1
            cover.append(lines[i])
            i += 1
        return cover, i

    @staticmethod
    def _collect_table(lines, i):
        rows = []
        n = len(lines)
        while i < n and lines[i].strip().startswith("|"):
            raw = lines[i].strip()
            if not re.fullmatch(r"[\s:\-|]+", raw):     # skip the |---|---| rule
                cells = [c.strip() for c in raw.strip("|").split("|")]
                rows.append(cells)
            i += 1
        return rows, i

    # -- main loop --------------------------------------------------------- #
    def build(self):
        lines = self.src.read_text(encoding="utf-8-sig").splitlines()
        n = len(lines)
        i = 0
        while i < n:
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            if RE_COVER_OPEN.match(line):
                cover, i = self._collect_cover(lines, i)
                self.add_cover(cover)
                self._pending_break = True       # cover ends with a page break
                continue

            if RE_PAGEBREAK.match(line):
                self._pending_break = True
                i += 1
                continue

            if line.startswith("# ") and not line.startswith("## "):
                self.add_title(line[2:].strip())
                i += 1
                continue

            if line.startswith("#### "):
                self.add_heading(line[5:].strip(), 3)
                i += 1
                continue

            if line.startswith("### "):
                self.add_heading(line[4:].strip(), 2)
                i += 1
                continue

            if line.startswith("## "):
                text = line[3:].strip()
                self.in_refs = "参考文献" in text
                self.add_heading(text, 1)
                i += 1
                continue

            match = RE_FIGURE.match(line)
            if match:
                self.add_figure(match.group(1).strip(), match.group(2).strip())
                i += 1
                continue

            # 表题：允许表题与表格之间隔一个空行（修复旧脚本的识别 bug）
            if RE_TABLE_CAPTION.match(line):
                j = self._next_nonblank(lines, i + 1)
                if j < n and lines[j].strip().startswith("|"):
                    self.add_table_caption(line)
                    i = j                       # 下一轮循环读取表格块
                    continue

            if line.startswith("|"):
                rows, i = self._collect_table(lines, i)
                if rows:
                    self.add_table(rows)
                continue

            if self.in_refs and RE_REF_LINE.match(line):
                self.add_reference(line)
                i += 1
                continue

            self.add_body(line)
            i += 1

        self.out.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(self.out))
        return self.out


def build(src, out):
    builder = ProposalBuilder(src, out)
    return builder.build()


def main(argv):
    src = Path(argv[1]) if len(argv) > 1 else DEFAULT_SRC
    out = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUT
    result = build(src, out)
    doc = Document(str(result))
    print("src : %s" % src)
    print("out : %s" % result)
    print("paragraphs: %d | tables: %d | images: %d"
          % (len(doc.paragraphs), len(doc.tables), len(doc.inline_shapes)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
