import urllib.request, urllib.parse, ssl, sys, re, html

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9,*;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", "replace"), r.geturl()

for arg in sys.argv[1:]:
    url, _, kws = arg.partition("|||")
    print("=" * 90)
    print("PAGE:", url)
    try:
        page, final = fetch(url)
    except Exception as e:
        print("  FETCH ERR:", type(e).__name__, e)
        continue
    print("  final:", final, "len:", len(page))
    plain = re.sub(r"<[^>]+>", " ", page)
    plain = html.unescape(re.sub(r"\s+", " ", plain))
    for kw in [k for k in kws.split(",") if k]:
        for m in re.finditer(re.escape(kw), plain, re.I):
            print(f"  [{kw}] ...{plain[max(0,m.start()-200):m.start()+260]}...")
            break
        else:
            print(f"  [{kw}] NOT FOUND in text")
    # print all pdf-ish links regardless
    pdfs = set()
    for m in re.finditer(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', page, re.I):
        pdfs.add(urllib.parse.urljoin(final, html.unescape(m.group(1))))
    if pdfs:
        print("  PDF-ish links:", len(pdfs))
        for p in list(pdfs)[:12]:
            print("    ", p)
