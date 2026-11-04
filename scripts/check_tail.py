# -*- coding: utf-8 -*-
from docx import Document
d = Document(r"D:\DSHCode\graduationThesis\deliverables\毕业设计任务书-v2-20261101.docx")
print("total paragraphs:", len(d.paragraphs), "tables:", len(d.tables))
for p in d.paragraphs[-3:]:
    print("TAIL:", repr(p.text[:100]))
# order check: signature after last table
body = d.element.body
kinds = [c.tag.split('}')[1] for c in body.iterchildren()]
print("body tail order:", kinds[-4:])
