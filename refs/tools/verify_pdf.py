import os, re, zlib, json

OUT = os.path.join("refs", "pdfs")

EXPECT = {
    "AE38NF87_Jimenez2024_SWE-bench.pdf": ["SWE-bench"],
    "65PKIFZ6_Hong2024_MetaGPT.pdf": ["MetaGPT"],
    "ANNZSKQM_Wang2024_CodeAct.pdf": ["CodeAct", "Executable Code Actions"],
    "IZ7ZP35I_Wang2025_OpenHands.pdf": ["OpenHands"],
    "ENWWAKKP_Yang2024_SWE-agent.pdf": ["SWE-agent"],
    "QQIJIJRN_Qian2024_ChatDev.pdf": ["ChatDev"],
    "FKUGWJ53_Pimentel2017_noWorkflow.pdf": ["noWorkflow"],
    "GF7S8GGG_Kagdi2007_MSR-survey.pdf": ["Mining Software Repositories", "survey"],
    "7WAR8TSF_Parnin2011_Resumption.pdf": ["Resumption", "interrupted"],
}

def text_of(path, max_streams=60):
    data = open(path, "rb").read()
    chunks = []
    for i, m in enumerate(re.finditer(rb"stream\r?\n", data)):
        if i >= max_streams:
            break
        start = m.end()
        end = data.find(b"endstream", start)
        if end < 0:
            continue
        raw = data[start:end]
        try:
            chunks.append(zlib.decompress(raw))
        except Exception:
            chunks.append(raw)
    return b"\n".join(chunks).decode("latin-1", "replace")

print(f"{'file':46s} {'bytes':>9s}  matched / first-hit")
print("-" * 110)
report = {}
for fn, keys in EXPECT.items():
    p = os.path.join(OUT, fn)
    txt = text_of(p)
    flat = re.sub(r"\s+", " ", txt)
    hits = [k for k in keys if k.lower() in flat.lower()]
    snippet = ""
    if hits:
        i = flat.lower().find(hits[0].lower())
        snippet = flat[max(0, i - 60): i + 90]
    report[fn] = {"matched": hits, "ok": len(hits) > 0}
    print(f"{fn:46s} {os.path.getsize(p):9d}  {hits}")

print("\n--- sample snippets ---")
for fn, r in report.items():
    if r["ok"]:
        p = os.path.join(OUT, fn)
        flat = re.sub(r"\s+", " ", text_of(p))
        i = flat.lower().find(r["matched"][0].lower())
        print(fn, "::", flat[max(0, i - 70): i + 110].strip()[:180])

ok = sum(1 for r in report.values() if r["ok"])
print(f"\nVERIFIED {ok}/{len(EXPECT)}")
