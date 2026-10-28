# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Emu
p = r"D:\DSHCode\graduationThesis\deliverables\毕业设计开题报告-v1-20261027.docx"
d = Document(p)
sec = d.sections[0]
tw = Emu(sec.page_width - sec.left_margin - sec.right_margin).cm
print("text width:", round(tw, 2), "cm")
for i, t in enumerate(d.tables):
    w = sum(c.width.cm for c in t.rows[0].cells if c.width)
    hdr = " | ".join(c.text[:8] for c in t.rows[0].cells)
    print(f"table{i+1}: rows={len(t.rows)} cols={len(t.columns)} width={round(w,2)}cm overflow={w > tw + 0.1} [{hdr}]")
