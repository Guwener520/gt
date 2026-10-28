#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Inspect a proposal .docx: counts, citations, structure, leftovers.

Usage:
    python check_proposal.py [docx path]

Default path: deliverables/毕业设计开题报告-v2-20261027.docx

Differences from the previous version
-------------------------------------
* takes the docx path from argv (no hard-coded, mojibake-prone path);
* counts Chinese characters inside table cells as well (the old version only
  walked ``document.paragraphs``, which silently dropped ~900 characters and
  made the word count look wrong);
* walks the body in document order so citation first-appearance order is correct
  across paragraphs *and* tables;
* checks the OOXML structure the reviewer asked about (Heading pStyle, tblHeader,
  cantSplit, superscript runs, header/footer parts, PAGE field parts);
* ASCII-safe output: no emoji, no box-drawing, no arrows.

Exit code: 0 when the file was read and checked (the PASS/FAIL verdict is printed),
2 when the docx cannot be opened. A non-zero exit is reserved for I/O problems so
the script can sit inside build pipelines.
"""
import re
import sys
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCX = ROOT / "deliverables" / "毕业设计开题报告-v2-20261027.docx"

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LATIN_WORD_RE = re.compile(r"[A-Za-z]+(?:['\-][A-Za-z]+)*")
CITE_RE = re.compile(r"\[\d+(?:\s*[,，\-–－]\s*\d+)*\]")
REF_LINE_RE = re.compile(r"^\[\d+\]")
FIG_CAPTION_RE = re.compile(r"^图\s*\d+(?:\s*[-－.．]\s*\d+)?")
TAB_CAPTION_RE = re.compile(r"^表\s*\d+(?:\s*[-－.．]\s*\d+)?")
MD_LEFTOVER_RE = re.compile(r"\*\*|!\[|^#{1,6}\s|\]\(|<!--")
CITE_SPLIT_RE = re.compile(r"[,，]")
CITE_RANGE_RE = re.compile(r"[-–－]")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def iter_blocks(doc):
    """Yield body-level Paragraph / Table objects in document order."""
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def table_paragraph_texts(table):
    """Every paragraph text inside a table, without merged-cell duplication."""
    for p in table._tbl.iter(qn("w:p")):
        yield "".join(node.text or "" for node in p.iter(qn("w:t")))


def expand_citation(group):
    """'12,35' / '23-27' -> [12, 35] / [23, 24, 25, 26, 27]."""
    numbers = []
    for part in CITE_SPLIT_RE.split(group):
        part = part.strip()
        if not part:
            continue
        if CITE_RANGE_RE.search(part):
            bounds = CITE_RANGE_RE.split(part)
            if len(bounds) == 2 and bounds[0].strip().isdigit() and bounds[1].strip().isdigit():
                low, high = int(bounds[0]), int(bounds[1])
                if low <= high:
                    numbers.extend(range(low, high + 1))
                else:
                    numbers.extend(range(high, low + 1))
        elif part.isdigit():
            numbers.append(int(part))
    return numbers


def read_zip_text(path, member):
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.read(member).decode("utf-8", "replace")
    except (KeyError, zipfile.BadZipFile, OSError):
        return ""


def find_pages(path):
    app_xml = read_zip_text(path, "docProps/app.xml")
    match = re.search(r"<Pages>\s*(\d+)\s*</Pages>", app_xml)
    return match.group(1) if match else "n/a"


def count_in_xml(xml_text, tag):
    return len(re.findall(r"<w:%s[\s/>]" % tag, xml_text))


def strip_tags(xml_text):
    return re.sub(r"<[^>]+>", "", xml_text)


def verdict(ok):
    return "OK" if ok else "FAIL"


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def check(path):
    problems = []
    doc = Document(str(path))

    # ---------- content collection (document order) ---------- #
    body_paragraphs = []
    table_texts = []
    ref_count = 0
    order = []
    figure_captions = []
    table_captions = []

    for block in iter_blocks(doc):
        if isinstance(block, Paragraph):
            text = block.text
            body_paragraphs.append(text)
            stripped = text.strip()
            # captions are centered paragraphs; body text such as
            # "图 3-1 之后……" must not be mistaken for a caption
            centered = block.alignment == WD_ALIGN_PARAGRAPH.CENTER
            if REF_LINE_RE.match(stripped):
                ref_count += 1
                continue                       # reference list: no citations here
            if centered and FIG_CAPTION_RE.match(stripped):
                figure_captions.append(stripped)
            if centered and TAB_CAPTION_RE.match(stripped):
                table_captions.append(stripped)
            for match in CITE_RE.finditer(text):
                for number in expand_citation(match.group(0)[1:-1]):
                    if number not in order:
                        order.append(number)
        else:
            for text in table_paragraph_texts(block):
                table_texts.append(text)
                for match in CITE_RE.finditer(text):
                    for number in expand_citation(match.group(0)[1:-1]):
                        if number not in order:
                            order.append(number)

    body_text = "\n".join(body_paragraphs)
    table_text = "\n".join(table_texts)
    all_text = body_text + "\n" + table_text

    cjk_body = len(CJK_RE.findall(body_text))
    cjk_table = len(CJK_RE.findall(table_text))
    cjk_total = cjk_body + cjk_table
    latin_words = len(LATIN_WORD_RE.findall(all_text))
    word_estimate = cjk_total + latin_words
    pages = find_pages(path)

    # ---------- OOXML structure ---------- #
    document_xml = read_zip_text(path, "word/document.xml")
    heading_styles = re.findall(r'<w:pStyle w:val="(Heading[0-9])"', document_xml)
    tbl_header_count = count_in_xml(document_xml, "tblHeader")
    cant_split_count = count_in_xml(document_xml, "cantSplit")
    superscript_count = len(re.findall(
        r'<w:vertAlign w:val="superscript"', document_xml))
    header_refs = count_in_xml(document_xml, "headerReference")
    footer_refs = count_in_xml(document_xml, "footerReference")

    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    header_parts = [n for n in names if re.match(r"word/header\d*\.xml$", n)]
    footer_parts = [n for n in names if re.match(r"word/footer\d*\.xml$", n)]
    header_text = "".join(strip_tags(read_zip_text(path, part))
                          for part in header_parts).strip()
    footer_xml = "".join(read_zip_text(path, part) for part in footer_parts)
    footer_instr = re.findall(r'<w:instrText[^>]*>([^<]*)</w:instrText>', footer_xml)
    field_parts = {
        kind: len(re.findall(r'w:fldCharType="%s"' % kind, footer_xml))
        for kind in ("begin", "separate", "end")
    }

    # per-table row protection (approximate "table split by page" check)
    table_stats = []
    for tbl in re.findall(r"<w:tbl>.*?</w:tbl>", document_xml, re.S):
        rows = len(re.findall(r"<w:tr[\s>]", tbl))
        protected = len(re.findall(r"<w:cantSplit", tbl))
        first_row = tbl[:tbl.find("</w:tr>") + 7] if "</w:tr>" in tbl else tbl
        has_header = "<w:tblHeader" in first_row
        table_stats.append((rows, protected, has_header))

    # ---------- citation validation ---------- #
    ascending = order == sorted(order)
    uncited = sorted(set(range(1, ref_count + 1)) - set(order))
    out_of_range = sorted(number for number in order if number < 1 or number > ref_count)
    if not ascending:
        problems.append("citation first-appearance order is not ascending")
    if uncited:
        problems.append("uncited references: %s" % uncited)
    if out_of_range:
        problems.append("citations out of range: %s" % out_of_range)

    # ---------- leftovers / quotes ---------- #
    leftovers = [(idx, text[:60]) for idx, text in enumerate(body_paragraphs)
                 if MD_LEFTOVER_RE.search(text)]
    leftovers += [(idx, text[:60]) for idx, text in enumerate(table_texts)
                  if MD_LEFTOVER_RE.search(text)]
    straight_double = all_text.count('"')
    straight_single = all_text.count("'")
    curly_open = all_text.count("\u201c")
    curly_close = all_text.count("\u201d")
    if leftovers:
        problems.append("residual Markdown markers: %d" % len(leftovers))
    if straight_double:
        problems.append('straight double quotes: %d' % straight_double)

    # ---------- structure expectations ---------- #
    if not heading_styles:
        problems.append("no Heading-styled paragraph (navigation pane / TOC broken)")
    if doc.tables and tbl_header_count < len(doc.tables):
        problems.append("tables without <w:tblHeader/>: %d"
                        % (len(doc.tables) - tbl_header_count))
    if cant_split_count < sum(stat[0] for stat in table_stats):
        problems.append("rows without <w:cantSplit/>: %d"
                        % (sum(stat[0] for stat in table_stats) - cant_split_count))
    if not header_parts:
        problems.append("no header part (页眉缺失)")
    if not footer_parts:
        problems.append("no footer part (页脚缺失)")
    if not footer_instr or "PAGE" not in " ".join(footer_instr):
        problems.append("footer PAGE field missing")
    elif field_parts["begin"] != field_parts["separate"] or field_parts["begin"] != field_parts["end"]:
        problems.append("PAGE field is incomplete (begin/separate/end mismatch)")

    # ---------- report ---------- #
    print("=" * 70)
    print("FILE")
    print("  path: %s" % path)
    print("=" * 70)
    print("COUNTS")
    print("  paragraphs (body)          : %d" % len(body_paragraphs))
    print("  paragraphs (in tables)     : %d" % len(table_texts))
    print("  tables                     : %d" % len(doc.tables))
    print("  images                     : %d" % len(doc.inline_shapes))
    print("  references                 : %d" % ref_count)
    print("  cjk chars (paragraphs)     : %d" % cjk_body)
    print("  cjk chars (tables)         : %d" % cjk_table)
    print("  cjk chars (total)          : %d" % cjk_total)
    print("  latin words                : %d" % latin_words)
    print("  word-count estimate        : %d  (cjk + latin words)" % word_estimate)
    print("  pages (docProps/app.xml)   : %s" % pages)

    print("-" * 70)
    print("CITATIONS")
    print("  first-appearance order     : %s" % order)
    print("  monotonic ascending        : %s" % verdict(ascending))
    print("  uncited references         : %s" % (uncited if uncited else "none"))
    print("  out-of-range citations     : %s" % (out_of_range if out_of_range else "none"))

    print("-" * 70)
    print("CAPTIONS")
    print("  figure captions (%d):" % len(figure_captions))
    for caption in figure_captions:
        print("    %s" % caption)
    print("  table captions (%d):" % len(table_captions))
    for caption in table_captions:
        print("    %s" % caption)
    if figure_captions and len(figure_captions) != len(doc.inline_shapes):
        print("  note: %d figure captions vs %d images"
              % (len(figure_captions), len(doc.inline_shapes)))

    print("-" * 70)
    print("LEFTOVERS")
    print("  residual markdown markers  : %d" % len(leftovers))
    for idx, snippet in leftovers[:10]:
        print("    #%d %s" % (idx, snippet))
    print("  straight double quotes     : %d" % straight_double)
    print("  straight single quotes     : %d" % straight_single)
    print("  curly quotes (open/close)  : %d / %d" % (curly_open, curly_close))

    print("-" * 70)
    print("DOCX STRUCTURE")
    print("  Heading-styled paragraphs  : %d  (H1=%d, H2=%d, other=%d)"
          % (len(heading_styles),
             heading_styles.count("Heading1"),
             heading_styles.count("Heading2"),
             len(heading_styles) - heading_styles.count("Heading1")
             - heading_styles.count("Heading2")))
    print("  tblHeader elements         : %d" % tbl_header_count)
    print("  cantSplit elements         : %d" % cant_split_count)
    print("  superscript runs           : %d" % superscript_count)
    print("  headerReference            : %d  (header parts: %d)"
          % (header_refs, len(header_parts)))
    print("  footerReference            : %d  (footer parts: %d)"
          % (footer_refs, len(footer_parts)))
    print("  header text                : %s"
          % (header_text if header_text else "<empty>"))
    print("  footer PAGE field parts    : begin=%d instrText=%s separate=%d end=%d"
          % (field_parts["begin"],
             "PAGE" if any("PAGE" in item for item in footer_instr) else "missing",
             field_parts["separate"], field_parts["end"]))
    print("  tables row protection      :")
    for idx, (rows, protected, has_header) in enumerate(table_stats, start=1):
        print("    table %d: rows=%d cantSplit=%d headerRepeat=%s -> %s"
              % (idx, rows, protected, "yes" if has_header else "no",
                 "fully protected" if protected >= rows else "rows may split"))

    print("=" * 70)
    if problems:
        print("RESULT: FAIL (%d problem(s))" % len(problems))
        for item in problems:
            print("  - %s" % item)
    else:
        print("RESULT: PASS (no problems found)")
    print("=" * 70)
    return 0


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_DOCX
    if not path.exists():
        print("ERROR: file not found: %s" % path)
        return 2
    return check(path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
