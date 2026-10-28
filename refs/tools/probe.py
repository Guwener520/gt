import urllib.request, ssl, sys, json

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def probe(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read(2048)
            ct = r.headers.get("Content-Type", "")
            cl = r.headers.get("Content-Length", "?")
            magic = data[:5]
            return dict(url=url, status=r.status, ct=ct, cl=cl,
                        is_pdf=magic.startswith(b"%PDF"),
                        final=r.geturl())
    except Exception as e:
        return dict(url=url, status="ERR", err=f"{type(e).__name__}: {e}")

urls = sys.argv[1:]
for u in urls:
    print(json.dumps(probe(u), ensure_ascii=False))
