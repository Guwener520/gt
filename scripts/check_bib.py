# -*- coding: utf-8 -*-
from pathlib import Path
import re
p = Path(r"D:\DSHCode\graduationThesis\deliverables\任务书参考文献-v1.bib")
t = p.read_text(encoding="utf-8")
entries = re.findall(r"@(\w+)\{([^,]+),", t)
print("bib entries:", len(entries))
print("kinds:", {k: sum(1 for a, _ in entries if a == k) for k, _ in entries})
print("sample keys:", [k for _, k in entries][:5])
