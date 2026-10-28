# -*- coding: utf-8 -*-
import re
from docx import Document
from docx.shared import Pt

path = r"D:\DSHCode\graduationThesis\deliverables\毕业设计任务书-v1-20261027.docx"
d = Document(path)

bad = []
for p in d.paragraphs:
    if re.search(r"\*\*|^\s*\||^#{1,3}\s", p.text):
        bad.append(p.text[:60])
for t in d.tables:
    for r in t.rows:
        for c in r.cells:
            if "**" in c.text:
                bad.append("TABLE:" + c.text[:40])
print("markdown artifacts:", bad if bad else "none")

# heading formatting
for p in d.paragraphs:
    if p.runs and p.runs[0].bold and p.runs[0].font.size and p.runs[0].font.size.pt >= 14:
        r = p.runs[0]
        print(f"H: {p.text} | font={r.font.name} size={r.font.size.pt} bold={r.bold}")

# reference paragraphs formatting
refs = [p for p in d.paragraphs if re.match(r"^\[\d+\]", p.text)]
print("refs:", len(refs))
if refs:
    p = refs[0]
    pf = p.paragraph_format
    print("  size:", p.runs[0].font.size.pt, "left_indent:", round(pf.left_indent.cm,2) if pf.left_indent else None,
          "first_line:", round(pf.first_line_indent.cm,2) if pf.first_line_indent else None,
          "spacing:", pf.line_spacing_rule)
    print("  sample:", p.text[:90])

# body paragraph formatting sample
body = [p for p in d.paragraphs if len(p.text) > 120 and not re.match(r"^\[\d+\]", p.text)]
b = body[0]
print("body sample:", b.text[:40], "| indent cm:", round(b.paragraph_format.first_line_indent.cm,2),
      "| spacing:", b.paragraph_format.line_spacing_rule, "| align:", b.paragraph_format.alignment)

# citation coverage: every [n] in body exists in refs
nums = set()
for p in d.paragraphs:
    if not re.match(r"^\[\d+\]", p.text):
        for m in re.findall(r"\[(\d+)\]", p.text):
            nums.add(int(m))
print("citations used:", sorted(nums))
print("refs defined:", len(refs))
print("missing:", sorted(set(range(1, len(refs)+1)) - nums))
