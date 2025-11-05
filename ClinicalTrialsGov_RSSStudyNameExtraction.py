#!/usr/bin/env python3
# extract_nct_from_rss.py
# Usage:
#   python extract_nct_from_rss.py "https://clinicaltrials.gov/api/rss?aggFilters=ages%3Aadult+older%2Chealthy%3Ay%2Cphase%3A0+1+2+3+4+NA%2CstudyType%3Aint&dateField=LastUpdatePostDate"

import sys, re, requests
import xml.etree.ElementTree as ET

NCT_RE = re.compile(r"NCT\d{8}")

def extract_ncts(rss_url: str):
    r = requests.get(rss_url, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    ncts = set()
    for item in root.findall(".//item"):
        parts = []
        for tag in ("link", "guid", "title", "description"):
            el = item.find(tag)
            if el is not None and el.text:
                parts.append(el.text)
        blob = " ".join(parts)
        ncts.update(NCT_RE.findall(blob))
    return sorted(ncts)

def main():


if __name__ == "__main__":
    main()
