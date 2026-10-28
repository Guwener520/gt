import urllib.request, urllib.parse, http.cookiejar, ssl, os, re, json

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
OUT = os.path.join("refs", "pdfs")

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(jar),
    urllib.request.HTTPSHandler(context=CTX),
)

def req(url, referer=None, accept="*/*"):
    h = {"User-Agent": UA, "Accept": accept, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}
    if referer:
        h["Referer"] = referer
    return urllib.request.Request(url, headers=h)

def get(url, referer=None, accept="*/*", timeout=60):
    return opener.open(req(url, referer, accept), timeout=timeout)

# check MetaGPT file header
p = os.path.join(OUT, "65PKIFZ6_Hong2024_MetaGPT.pdf")
with open(p, "rb") as f:
    print("MetaGPT head:", f.read(8), "size:", os.path.getsize(p))

for art in ["7474", "7567"]:
    print("\n===== article", art, "=====")
    abs_url = f"https://www.jos.org.cn/jos/article/abstract/{art}"
    try:
        r = get(abs_url, accept="text/html")
        page = r.read().decode("utf-8", "replace")
        print("abstract:", r.status, len(page), "cookies:", [c.name for c in jar])
        t = re.search(r"<title>(.*?)</title>", page, re.S)
        print("  title:", (t.group(1).strip() if t else "?")[:120])
    except Exception as e:
        print("abstract ERR", type(e).__name__, e)
        continue
    for pdf_url in [f"https://www.jos.org.cn/jos/article/pdf/{art}",
                    f"https://www.jos.org.cn/jos/article/html/{art}"]:
        try:
            r = get(pdf_url, referer=abs_url, accept="application/pdf,text/html")
            data = r.read()
            print(f"  {pdf_url} -> {r.status} ct={r.headers.get('Content-Type')} len={len(data)} pdf={data[:5]==b'%PDF'}")
            if data[:5] == b"%PDF":
                dest = os.path.join(OUT, f"JOS{art}.pdf")
                with open(dest, "wb") as f:
                    f.write(data)
                print("   SAVED", dest, len(data))
        except Exception as e:
            print(f"  {pdf_url} ERR", type(e).__name__, e)
