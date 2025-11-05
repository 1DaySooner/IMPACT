#!/usr/bin/env python3
# print_study_institution.py
# Usage:
#   python print_study_institution.py NCT05563610 NCT07152379
#   # or hardcode ids = [...] below and just run
# We need to following fields:
# Short Name (extract_studyTitles),Study Name(extract_studyTitles), Status (extract_studyStatus), 
# Challenge Agent (added),
# Institution(s) (extract_institution),
# Country (Use lat/long instead), Start Date, Completion Date (not required for now),
# Registry ID (extract_institution), Brief Summary (extract_briefSummary)

import sys, requests, re, csv
import xml.etree.ElementTree as ET

API_BASE = "https://clinicaltrials.gov/api/v2"
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


def get_study(nct_id: str) -> dict:
    r = requests.get(f"{API_BASE}/studies/{nct_id}", timeout=30)
    if r.status_code == 404:
        return {}
    r.raise_for_status()
    data = r.json() or {}
    return data

def extract_nct_id_info(study: dict) -> list:
    ps = study.get("protocolSection", {}) or {}
    idMod = ps.get("identificationModule",{}) or {}
    
    leadOrg = idMod.get("organization",{}).get("fullName",[])
    studyID = idMod.get("nctId") or ""
    officialTitle = idMod.get("officialTitle") or ""
    shortTitle = idMod.get("briefTitle") or ""
    
    statMod = ps.get("statusModule",{}) or {}
    currentOverallStatus = statMod.get("overallStatus", "") or "" 
    lastKnownStatus = statMod.get("lastKnownStatus", "") or ""
    lastKnownStatusDate = statMod.get("statusVerifiedDate", "") or "" 
    currentDateMod = statMod.get("startDateStruct", "") or ""
    currentDate = currentDateMod.get("date", "") or ""
    currentDateType = currentDateMod.get("type", "") or "" 
    
    contactMod = ps.get("contactsLocationsModule", {}) or {} 
    contactList = contactMod.get("centralContacts", {}) or {} 
    contacts = []
    for cont in contactList: 
        contName = cont.get("name") or "" 
        contEmail = cont.get("email") or ""
        cont_str = f"{contEmail} ({contName})"
        contacts.append(cont_str)
    contacts_str = "; ".join(contacts)

    siteList = contactMod.get("locations", "") or ""
    sites = []
    for loc in siteList:
        facility = (loc.get("facility") or "").strip()
    
        # geoPoint may be missing or partially populated
        geo = loc.get("geoPoint") or {}
        lat = geo.get("lat")
        lon = geo.get("lon")
    
        site_str = f"{facility} ({lat}, {lon})" if lat and lon else facility
        sites.append(site_str)
    sites_str = "; ".join(sites)
    
    descMod = ps.get("descriptionModule",{}) or {}
    briefSummary = descMod.get("briefSummary", "") or ""
    
    eligMod = ps.get("eligibilityModule", {}) or {}
    sex = eligMod.get("sex","") or "" 
    minAge = eligMod.get("minimumAge", "") or ""
    maxAge = eligMod.get("maximumAge", "") or ""
    
    condMod = ps.get("conditionsModule", {}) or []
    keywords = condMod.get("keywords", []) or []  # usually a list of strings
    lower_keywords = [k.lower() for k in keywords]
    
    likely_challenge = "False"
    if any("human challenge" in k for k in lower_keywords):
        likely_challenge = "True"
    if any("controlled human infection" in k for k in lower_keywords):
        likely_challenge = "True"
    if ("human challenge" in briefSummary): 
        likely_challenge = "True"
         
    challenge_agent = condMod.get("conditions")[0]
    
    return [studyID, leadOrg, officialTitle, shortTitle, 
            sites_str, contacts_str,  
            currentOverallStatus, lastKnownStatus, lastKnownStatusDate, 
            currentDateType, currentDate, briefSummary, 
            sex, minAge, maxAge, 
            likely_challenge, challenge_agent]

def main(ids):
    
    out = "C:\\Users\\circe\\Downloads\\historical_output.csv"
    
    fieldnames = [
    "studyID", "leadOrg", "officialTitle","shortTitle",
    "sites","contacts",
    "currentOverallStatus","lastKnownStatus","lastKnownStatusDate",
    "currentDateType","currentDate","briefSummary",
    "sex","minAge","maxAge",
    "likely_challenge","challenge_agent"
    ]
    
    with open(out, "w", newline="\n", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(fieldnames)
        for raw in ids:
            nct = raw.strip().upper()
            try:
                study = get_study(nct)
                if not study:
                    print(f"{nct}\tNOT FOUND")
                    continue
                details = extract_nct_id_info(study)
                w.writerow(details)
            except requests.HTTPError as e:
                print(f"{nct}\tHTTP {e.response.status_code}")
            except Exception as e:
                print(f"{nct}\tERROR: {e}") 
    


if __name__ == "__main__":
    # url = sys.argv[1] if len(sys.argv) > 1 else (
    #     "https://clinicaltrials.gov/api/rss?aggFilters=ages%3Aadult+older%2Chealthy%3Ay%2Cphase%3A0+1+2+3+4+NA%2CstudyType%3Aint&dateField=LastUpdatePostDate"
    # )
    # ids = extract_ncts(url)
    ids = []
    with open("C:\\Users\\circe\\Downloads\\ctg-studies.csv", "r") as file: 
            reader = csv.reader(file)
            for row in reader: 
                ids.append(row[0])
    main(ids)