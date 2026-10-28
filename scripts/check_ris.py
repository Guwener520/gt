# -*- coding: utf-8 -*-
from pathlib import Path
p = Path(r"D:\DSHCode\graduationThesis\deliverables\任务书参考文献-v1.ris")
raw = p.read_bytes()
print("BOM:", raw[:3] == b"\xef\xbb\xbf", "| bytes:", len(raw))
txt = raw.decode("utf-8")
records = [b.strip() for b in txt.split("ER  - ") if b.strip()]
print("records:", len(records))
import collections
tys = collections.Counter()
keys = collections.Counter()
bad = []
for b in records:
    tags = [l[:2] for l in b.splitlines() if len(l) > 5 and l[2:6] == "  - "]
    tys[b.splitlines()[0].split("  - ")[1]] += 1
    for t in tags: keys[t] += 1
    if "TI  - " not in b: bad.append(b[:40])
print("types:", dict(tys))
print("tags:", dict(sorted(keys.items())))
print("records missing TI:", bad)
# chinese check
zh = [b for b in records if "LA  - zh-CN" in b]
print("chinese records:", len(zh))
print("sample zh:", [l for l in zh[0].splitlines() if l.startswith(("TI","AU","JO","DO"))])
print("--- first record ---")
print(records[0].strip()[:400])
