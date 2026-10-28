import urllib.request, urllib.parse, ssl, json, os, re, html

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
OUT = os.path.join("refs", "pdfs")

def get(url, timeout=120, headers=None):
    h = {"User-Agent": UA, "Accept": "application/pdf,text/html,*/*", "Accept-Language": "en-US,en;q=0.9"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    return urllib.request.urlopen(req, timeout=timeout, context=CTX)

def stream_to(url, dest):
    r = get(url)
    total = 0
    with open(dest, "wb") as f:
        while True:
            chunk = r.read(256 * 1024)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
    with open(dest, "rb") as f:
        head = f.read(5)
    if head != b"%PDF":
        raise ValueError("not a PDF")
    return total

# 1) retry MetaGPT with streaming
dest = os.path.join(OUT, "65PKIFZ6_Hong2024_MetaGPT.pdf")
try:
    n = stream_to("https://arxiv.org/pdf/2308.00352", dest)
    print("MetaGPT ok", n)
except Exception as e:
    print("MetaGPT ERR", type(e).__name__, e)

# 2) HAL GumTree: parse landing page for real file link
for land in ["https://hal.science/hal-01054552", "https://inria.hal.science/hal-01054552"]:
    try:
        r = get(land)
        page = r.read().decode("utf-8", "replace")
        print("HAL landing:", land, r.status, len(page))
        files = set()
        for m in re.finditer(r'href=["\']([^"\']*(?:/file/|/document|\.pdf)[^"\']*)["\']', page, re.I):
            files.add(urllib.parse.urljoin(r.geturl(), html.unescape(m.group(1))))
        print("  candidates:", list(files)[:10])
        ok = False
        for f in sorted(files):
            try:
                n = stream_to(f, os.path.join(OUT, "U9XIYLPZ_Falleri2014_GumTree.pdf"))
                print("  GumTree ok via", f, n)
                ok = True
                break
            except Exception as e:
                print("   fail", f, type(e).__name__, e)
        if ok:
            break
    except Exception as e:
        print("HAL ERR", land, type(e).__name__, e)

# 3) page counts for everything downloaded
print("\n--- page counts ---")
for fn in sorted(os.listdir(OUT)):
    if not fn.lower().endswith(".pdf"):
        continue
    p = os.path.join(OUT, fn)
    data = open(p, "rb").read()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    print(f"{fn:52s} {len(data)/1024/1024:6.2f} MB  pages~{pages}")
