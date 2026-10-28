import urllib.request, urllib.parse, ssl, sys, re, html

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9,*;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", "replace"), r.geturl()

def show(url, keywords):
    print("=" * 100)
    print("PAGE:", url)
    try:
        page, final = fetch(url)
    except Exception as e:
        print("  FETCH ERR:", type(e).__name__, e)
        return
    print("  final:", final, "len:", len(page))
    anchors = re.findall(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', page, re.S | re.I)
    hits = 0
    for href, text in anchors:
        plain = html.unescape(re.sub(r"<[^>]+>", " ", text))
        plain = re.sub(r"\s+", " ", plain).strip()
        blob = (href + " " + plain).lower()
        if any(k.lower() in blob for k in keywords):
            full = urllib.parse.urljoin(final, html.unescape(href))
            print("   HIT:", plain[:110], "->", full)
            hits += 1
            if hits >= 25:
                break
    if hits == 0:
        print("   (no anchor hits)")

# usage: pairs of  url|||kw1,kw2
for arg in sys.argv[1:]:
    url, _, kws = arg.partition("|||")
    show(url, [k for k in kws.split(",") if k])
