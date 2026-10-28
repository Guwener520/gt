import urllib.request, ssl, os, re, json

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
OUT = os.path.join("refs", "pdfs")

def head(url, timeout=40, extra=None):
    h = {"User-Agent": UA, "Accept": "application/pdf,*/*"}
    if extra:
        h.update(extra)
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            b = r.read(2048)
            return {"url": url, "status": r.status, "ct": r.headers.get("Content-Type"),
                    "pdf": b.startswith(b"%PDF"), "len": r.headers.get("Content-Length"),
                    "final": r.geturl()}
    except Exception as e:
        return {"url": url, "status": "ERR", "err": f"{type(e).__name__}: {e}"}

def stream_to(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/pdf,*/*"})
    with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
        n = 0
        with open(dest, "wb") as f:
            while True:
                c = r.read(256 * 1024)
                if not c:
                    break
                f.write(c)
                n += len(c)
    if open(dest, "rb").read(5) != b"%PDF":
        raise ValueError("not a PDF")
    return n

# 1) MetaGPT retries
print("--- MetaGPT retries ---")
for u in ["https://arxiv.org/pdf/2308.00352v7",
          "http://arxiv.org/pdf/2308.00352",
          "https://export.arxiv.org/pdf/2308.00352",
          "https://arxiv.org/pdf/2308.00352v6"]:
    try:
        n = stream_to(u, os.path.join(OUT, "65PKIFZ6_Hong2024_MetaGPT.pdf"))
        print("  ok", u, n)
        break
    except Exception as e:
        print("  fail", u, type(e).__name__, str(e)[:120])

# 2) candidate direct URLs for remaining papers
print("\n--- candidate probes ---")
cands = [
    "https://www.inf.usi.ch/faculty/lanza/Downloads/Robb2007a.pdf",
    "https://www.cs.ubc.ca/~rtholmes/papers/icse2021_grund.pdf",
    "https://web.eecs.umich.edu/~andrewjko/pubs/ko-chi2004-whyline.pdf",
    "http://www.cs.cmu.edu/~NatProg/papers/KoMyers_Whyline.pdf",
    "https://www.andrewjko.com/pubs/whyline.pdf",
    "https://www.cis.upenn.edu/~cheney/papers/prov-fnt.pdf",
]
for u in cands:
    print(json.dumps(head(u), ensure_ascii=False))

# 3) integrity check of downloaded files
print("\n--- integrity ---")
for fn in sorted(os.listdir(OUT)):
    if not fn.lower().endswith(".pdf"):
        continue
    p = os.path.join(OUT, fn)
    d = open(p, "rb").read()
    tail = d[-2048:]
    counts = re.findall(rb"/Type\s*/Pages[^>]*?/Count\s+(\d+)", d)
    if not counts:
        counts = re.findall(rb"/Count\s+(\d+)", d)
    print(f"{fn:50s} {len(d)/1048576:6.2f}MB eof={b'%%EOF' in tail} count={counts[:3]}")
