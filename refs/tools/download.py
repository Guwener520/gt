import urllib.request, ssl, json, os, sys, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

OUT = os.path.join("refs", "pdfs")
os.makedirs(OUT, exist_ok=True)

# key: (filename, [urls to try])
TARGETS = {
    "AE38NF87": ("AE38NF87_Jimenez2024_SWE-bench.pdf", ["https://arxiv.org/pdf/2310.06770"]),
    "65PKIFZ6": ("65PKIFZ6_Hong2024_MetaGPT.pdf", ["https://arxiv.org/pdf/2308.00352"]),
    "ANNZSKQM": ("ANNZSKQM_Wang2024_CodeAct.pdf", ["https://arxiv.org/pdf/2402.01030"]),
    "IZ7ZP35I": ("IZ7ZP35I_Wang2025_OpenHands.pdf", ["https://arxiv.org/pdf/2407.16741"]),
    "ENWWAKKP": ("ENWWAKKP_Yang2024_SWE-agent.pdf", ["https://arxiv.org/pdf/2405.15793"]),
    "QQIJIJRN": ("QQIJIJRN_Qian2024_ChatDev.pdf", ["https://aclanthology.org/2024.acl-long.810.pdf"]),
    "GF7S8GGG": ("GF7S8GGG_Kagdi2007_MSR-survey.pdf", ["http://www.cs.kent.edu/~jmaletic/papers/JSME07-survey.pdf"]),
    "FKUGWJ53": ("FKUGWJ53_Pimentel2017_noWorkflow.pdf", ["https://vldb.org/pvldb/vol10/p1841-pimentel.pdf"]),
    "U9XIYLPZ": ("U9XIYLPZ_Falleri2014_GumTree.pdf", [
        "https://hal.science/hal-01054552/document",
        "https://hal.science/hal-01054552/file/main.pdf",
        "https://inria.hal.science/hal-01054552/document",
    ]),
    "7WAR8TSF": ("7WAR8TSF_Parnin2011_Resumption.pdf", [
        "https://link.springer.com/content/pdf/10.1007/s11219-010-9104-9.pdf",
    ]),
}

def try_download(url, dest):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"not a PDF (content-type={r.headers.get('Content-Type')}, first={data[:40]!r})")
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)

results = []
for key, (fname, urls) in TARGETS.items():
    dest = os.path.join(OUT, fname)
    rec = {"key": key, "file": fname}
    for url in urls:
        try:
            n = try_download(url, dest)
            rec.update(status="ok", bytes=n, url=url)
            break
        except Exception as e:
            rec.setdefault("tried", []).append({"url": url, "err": f"{type(e).__name__}: {e}"})
    else:
        rec["status"] = "failed"
    results.append(rec)
    print(json.dumps(rec, ensure_ascii=False))

with open(os.path.join("refs", "download-results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
