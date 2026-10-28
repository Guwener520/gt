import urllib.request, urllib.parse, json, ssl

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def get(url, timeout=30, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json,*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        b = r.read()
        return b if raw else json.loads(b.decode("utf-8", "replace"))

def fatcat(doi):
    u = "https://api.fatcat.wiki/v0/release/lookup?doi=" + urllib.parse.quote(doi) + "&expand=files"
    try:
        d = get(u)
        out = []
        for f in d.get("files") or []:
            for uu in f.get("urls") or []:
                out.append({"url": uu.get("url"), "rel": uu.get("rel")})
        return {"fatcat": out[:8], "fatcat_title": d.get("title")}
    except Exception as e:
        return {"fatcat_err": f"{type(e).__name__}: {e}"}

def openalex(doi):
    u = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi)
    try:
        d = get(u)
        locs = (d.get("locations") or [])
        res = []
        for l in locs:
            res.append({"pdf": l.get("pdf_url"), "land": l.get("landing_page_url"),
                        "oa": l.get("is_oa"), "src": ((l.get("source") or {}) or {}).get("display_name")})
        return {"oa_title": d.get("title"), "oa_locs": res[:8],
                "oa_best": (d.get("best_oa_location") or {})}
    except Exception as e:
        return {"oa_err": f"{type(e).__name__}: {e}"}

def crossref(doi):
    u = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    try:
        d = get(u)["message"]
        return {"cr_title": (d.get("title") or [None])[0],
                "cr_url": d.get("URL"),
                "cr_links": [l.get("URL") for l in (d.get("link") or [])][:5]}
    except Exception as e:
        return {"cr_err": f"{type(e).__name__}: {e}"}

dois = {
    "7WAR8TSF": "10.1007/s11219-010-9104-9",
    "FKUGWJ53": "10.14778/3137765.3137789",
    "AXBIVLZ4": "10.1561/1900000006",
    "D4ZV6DT5": "10.1145/985692.985712",
    "UPWVDLDI": "10.1109/ICSE43902.2021.00135",
    "NPSPFW5U": "10.1016/j.entcs.2006.06.015",
    "JQ3KPVRH": "10.13328/j.cnki.jos.007474",
    "6D6DGRB4": "10.13328/j.cnki.jos.007567",
}

for key, doi in dois.items():
    rec = {"key": key, "doi": doi}
    rec.update(crossref(doi))
    rec.update(fatcat(doi))
    rec.update(openalex(doi))
    print(json.dumps(rec, ensure_ascii=False))
