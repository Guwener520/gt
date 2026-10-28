# -*- coding: utf-8 -*-
"""Build the Chinese undergraduate thesis task book (.docx) from thesis/task-book.md.

Usage: python build_taskbook_docx.py [src.md] [out.docx]
The Markdown file is the single source of truth: headings, paragraphs, tables and
**bold** runs are converted into an A4 academic layout (宋体/黑体, 小四, 1.5 倍行距).
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BODY_FONT = "宋体"
HEAD_FONT = "黑体"
BODY_SIZE = Pt(12)          # 小四
TABLE_SIZE = Pt(10.5)       # 五号

ROOT = Path(__file__).resolve().parents[1]


def set_run(run, text, font=BODY_FONT, size=BODY_SIZE, bold=False, color=None):
    run.text = text
    run.font.name = font
    run.font.size = size
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:eastAsia"), font)
    return run


def add_inline(paragraph, text, font=BODY_FONT, size=BODY_SIZE, base_bold=False):
    """Render **bold** segments inside one paragraph."""
    for idx, chunk in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if not chunk:
            continue
        set_run(paragraph.add_run(), chunk, font=font, size=size,
                bold=base_bold or idx % 2 == 1)


def add_body_paragraph(doc, text, indent_chars=2):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.first_line_indent = Pt(BODY_SIZE.pt * indent_chars)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_inline(p, text)
    return p


def add_heading(doc, text, level):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(14 if level == 1 else 10)
    pf.space_after = Pt(6 if level == 1 else 4)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    pf.keep_with_next = True
    size = Pt(14) if level == 1 else Pt(12)
    if level == 2:
        pf.space_before = Pt(10)
    set_run(p.add_run(), text, font=HEAD_FONT, size=size, bold=True)
    return p


def set_cell_borders(cell, sz=6):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tcPr.append(borders)


def shade_cell(cell, fill="F2F2F2"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_col_widths(table, widths_cm):
    table.autofit = False
    tblPr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    for row in table.rows:
        for idx, width in enumerate(widths_cm):
            if idx < len(row.cells):
                row.cells[idx].width = Cm(width)


def add_table(doc, rows):
    header, body = rows[0], rows[1:]
    table = doc.add_table(rows=1 + len(body), cols=len(header))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = True

    for j, text in enumerate(header):
        cell = table.rows[0].cells[j]
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].paragraph_format.space_before = Pt(2)
        cell.paragraphs[0].paragraph_format.space_after = Pt(2)
        add_inline(cell.paragraphs[0], text, font=HEAD_FONT, size=TABLE_SIZE, base_bold=True)
        shade_cell(cell)

    for i, row in enumerate(body, start=1):
        for j in range(len(header)):
            cell = table.rows[i].cells[j]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            value = row[j] if j < len(row) else ""
            centered = len(header) >= 3 and j == 0
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centered else WD_ALIGN_PARAGRAPH.LEFT
            add_inline(p, value, size=TABLE_SIZE)

    # 审核意见表：给签字行留出书写高度
    if len(header) >= 3 and "签字" in header[-1]:
        for row in table.rows[1:]:
            row.height = Cm(2.2)

    if len(header) == 2:
        set_col_widths(table, [3.4, 12.0])
    elif len(header) == 3 and any("签字" in h for h in header):
        set_col_widths(table, [3.4, 8.6, 3.4])
    elif len(header) == 3:
        set_col_widths(table, [4.6, 3.4, 7.4])
    elif len(header) == 4 and header[0] == "阶段":
        set_col_widths(table, [1.2, 3.8, 7.0, 3.4])
    elif len(header) == 4:
        set_col_widths(table, [3.0, 6.2, 3.0, 3.2])
    return table


def add_page_number_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    set_run(run, "", size=Pt(10.5))
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            fld = OxmlElement("w:fldChar")
            fld.set(qn("w:fldCharType"), kind)
            run._r.append(fld)
        else:
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = text
            run._r.append(instr)


def build(src: Path, out: Path):
    text = src.read_text(encoding="utf-8")
    lines = text.splitlines()

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = Cm(2.54)
    sec.bottom_margin = Cm(2.54)
    sec.left_margin = Cm(3.0)
    sec.right_margin = Cm(2.6)
    add_page_number_footer(sec)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = BODY_SIZE
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)

    in_refs = False
    i, n = 0, len(lines)
    while i < n:
        raw = lines[i]
        line = raw.strip()
        if not line:
            i += 1
            continue
        if line == "<!-- pagebreak -->":
            doc.add_page_break()
            i += 1
        elif line.startswith("# "):                     # document title
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(16)
            set_run(p.add_run(), line[2:].strip(), font=HEAD_FONT, size=Pt(18), bold=True)
            i += 1
        elif line.startswith("### "):                 # sub-section heading
            add_heading(doc, line[4:].strip(), level=2)
            i += 1
        elif re.match(r"^!\[(.*?)\]\((.+?)\)$", line):   # figure with caption
            m = re.match(r"^!\[(.*?)\]\((.+?)\)$", line)
            img_path = (src.parent / m.group(2)).resolve()
            if img_path.exists():
                doc.add_picture(str(img_path), width=Cm(15.4))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                doc.paragraphs[-1].paragraph_format.space_before = Pt(6)
                doc.paragraphs[-1].paragraph_format.space_after = Pt(3)
                cap = doc.add_paragraph()
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap.paragraph_format.space_after = Pt(10)
                cap.paragraph_format.space_before = Pt(0)
                set_run(cap.add_run(), m.group(1), size=TABLE_SIZE)
            else:
                add_body_paragraph(doc, "[图片缺失：" + m.group(2) + "]")
            i += 1
        elif line.startswith("## "):                  # section heading
            heading_text = line[3:].strip()
            in_refs = "参考文献" in heading_text
            add_heading(doc, heading_text, level=1)
            i += 1
        elif re.match(r"^表\s*\d+-\d+", line) and i + 1 < n and lines[i + 1].strip().startswith("|"):
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.space_before = Pt(8)
            cap.paragraph_format.space_after = Pt(3)
            cap.paragraph_format.keep_with_next = True
            set_run(cap.add_run(), line, size=TABLE_SIZE)
            i += 1
        elif line.startswith("|"):                    # table block
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.fullmatch(r"[\s:\-|]+", lines[i].strip()):
                    rows.append(cells)
                i += 1
            if rows:
                add_table(doc, rows)
                doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif in_refs and re.match(r"^\[\d+\]", line):
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
            pf.space_before = Pt(0)
            pf.space_after = Pt(2)
            pf.left_indent = Cm(0.85)
            pf.first_line_indent = Cm(-0.85)
            pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_inline(p, line, size=TABLE_SIZE)
            i += 1
        else:
            add_body_paragraph(doc, line)
            i += 1

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "thesis" / "task-book.md"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "deliverables" / "毕业设计任务书-v1-20261027.docx"
    print(build(src, out))
