#!/usr/bin/env python3
"""List papers on Flavio Calmon's Google Scholar profile that are missing from
publications.json, with full metadata from arXiv where available.

Run from the repository root:
    python3 .claude/skills/update-publications/find_new_papers.py [--pages N] [--since YEAR]

Prints a JSON array of candidates to stdout. Nothing is written to the repo.
"""
import argparse
import difflib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SCHOLAR_USER = "P8N_YH4AAAAJ"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")


def text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def norm(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def scholar_rows(pages):
    rows = []
    for page in range(pages):
        url = (f"https://scholar.google.com/citations?hl=en&user={SCHOLAR_USER}"
               f"&view_op=list_works&sortby=pubdate&cstart={page * 100}&pagesize=100")
        page_html = get(url)
        if "gsc_a_tr" not in page_html:
            sys.exit("Scholar returned no rows (rate-limited or captcha). Try again later.")
        for r in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', page_html, re.S):
            gray = [text(g) for g in re.findall(r'<div class="gs_gray">(.*?)</div>', r, re.S)]
            cid = re.search(r"citation_for_view=([^\"&]+)", r)
            year = re.search(r'gsc_a_h gsc_a_hc gs_ibl">(\d*)<', r)
            rows.append({
                "title": text(re.search(r'class="gsc_a_at">(.*?)</a>', r, re.S).group(1)),
                "scholar_authors": gray[0] if gray else "",
                "scholar_venue": gray[1] if len(gray) > 1 else "",
                "scholar_year": int(year.group(1)) if year and year.group(1) else None,
                "scholar_id": html.unescape(cid.group(1)) if cid else None,
            })
        time.sleep(2)
    return rows


def arxiv_entry(e):
    def field(tag):
        node = e.find(tag, NS)
        return " ".join(node.text.split()) if node is not None and node.text else None
    return {
        "arxiv_id": e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0],
        "title": field("a:title"),
        "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
        "published": field("a:published")[:10],
        "comment": field("arxiv:comment"),
        "journal_ref": field("arxiv:journal_ref"),
        "abstract": field("a:summary"),
    }


def arxiv_lookup(row):
    """Find the arXiv record for a Scholar row: by ID if Scholar shows one, else by title."""
    m = re.search(r"arXiv:\s*(\d{4}\.\d{4,5})", row["scholar_venue"])
    if m:
        query = "id_list=" + m.group(1)
    else:
        words = re.findall(r"[A-Za-z]{4,}", row["title"])[:8]
        query = "search_query=" + "+AND+".join("ti:" + urllib.parse.quote(w) for w in words) + "&max_results=5"
    root = ET.fromstring(get("http://export.arxiv.org/api/query?" + query))
    for e in root.findall("a:entry", NS):
        entry = arxiv_entry(e)
        # Only accept a match that has Calmon as an author and a near-identical title.
        if any("Calmon" in a for a in entry["authors"]) and \
                difflib.SequenceMatcher(None, norm(entry["title"]), norm(row["title"])).ratio() > 0.8:
            return entry
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=1, help="Scholar pages of 100 to scan (default 1)")
    ap.add_argument("--since", type=int, default=None, help="Only report papers from this year on")
    args = ap.parse_args()

    have = [norm(p["title"]) for p in json.load(open("publications.json"))]
    candidates = []
    for row in scholar_rows(args.pages):
        if args.since and (row["scholar_year"] or 0) < args.since:
            continue
        if difflib.get_close_matches(norm(row["title"]), have, 1, 0.8):
            continue
        row["arxiv"] = arxiv_lookup(row)
        candidates.append(row)
        time.sleep(3)  # arXiv asks for at most one request every 3 seconds
    json.dump(candidates, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
