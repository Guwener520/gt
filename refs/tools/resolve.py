import urllib.request, urllib.parse, json, sys, ssl

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def s2(doi):
    u = "https://api.semanticscholar.org/graph/v1/paper/DOI:" + urllib.parse.quote(doi) + "?fields=title,year,openAccessPdf,externalIds"
    try:
        d = get_json(u)
        oa = d.get("openAccessPdf") or {}
        return {"s2_title": d.get("title"), "s2_pdf": oa.get("url"), "s2_status": oa.get("status")}
    except Exception as e:
        return {"s2_err": f"{type(e).__name__}: {e}"}

def unpaywall(doi, email="dsh.agent@proton.me"):
    u = "https://api.unpaywall.org/v2/" + urllib.parse.quote(doi) + "?email=" + email
    try:
        d = get_json(u)
        locs = d.get("oa_locations") or []
        return {
            "upw_is_oa": d.get("is_oa"),
            "upw_best": (d.get("best_oa_location") or {}).get("url_for_pdf")
                        or (d.get("best_oa_location") or {}).get("url"),
            "upw_all": [{"pdf": l.get("url_for_pdf"), "url": l.get("url"),
                         "host": l.get("host_type"), "ver": l.get("version")} for l in locs[:6]],
        }
    except Exception as e:
        return {"upw_err": f"{type(e).__name__}: {e}"}

dois = {
    "7WAR8TSF": "10.1007/s11219-010-9104-9",
    "FKUGWJ53": "10.14778/3137765.3137789",
    "AXBIVLZ4": "10.1561/1900000006",
    "D4ZV6DT5": "10.1145/985692.985712",
    "UPWVDLDI": "10.1109/ICSE43902.2021.00135",
    "U9XIYLPZ": "10.1145/2642937.2642982",
    "NPSPFW5U": "10.1016/j.entcs.2006.06.015",
    "GF7S8GGG": "10.1002/smr.344",
    "JQ3KPVRH": "10.13328/j.cnki.jos.007474",
    "6D6DGRB4": "10.13328/j.cnki.jos.007567",
    "QQIJIJRN": "10.18653/v1/2024.acl-long.810",
}

for key, doi in dois.items():
    rec = {"key": key, "doi": doi}
    rec.update(s2(doi))
    rec.update(unpaywall(doi))
    print(json.dumps(rec, ensure_ascii=False))
