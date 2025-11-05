# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 11:50:00 2025

@author: circe
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

API = 'https://www.isrctn.com/api/query/format/default?q=conditionCategory:"Infections and Infestations"'

def get_isrctn_to_title():
    r = requests.get(API)
    if r.status_code == 404:
        return {}
    root = ET.fromstring(r.content)

    def local(tag: str) -> str:
        return tag.split('}', 1)[-1]

    out = {}
    for full_trial in root:
        if local(full_trial.tag) != "fullTrial":
            continue
        isrctn_val = None
        title_val = None

        for child in full_trial:
            if local(child.tag) == "trial":
                # grab isrctn and title by walking children
                for node in child:
                    tag = local(node.tag)
                    if tag == "isrctn":
                        isrctn_val = (node.text or "").strip()
                    elif tag == "trialDescription":
                        for sub in node:
                            if local(sub.tag) == "title":
                                title_val = (sub.text or "").strip()
                    elif tag == "contactDetails": 
                        for sub in node: 
                            if local(sub.tag) == "contactTypes": 
                                for sub_sub in sub: 
                                    if local(sub_sub) == ""

        if isrctn_val and title_val:
            out[isrctn_val] = title_val
    return out

out = get_isrctn_to_title()
print(out)

# def parse_trials(root):
#     trials = []
#     for trial in root.findall('.//isrctn'):
#         def text(tag):
#             el = trial.find(tag)
#             return el.text.strip() if el is not None and el.text else None

#         trials.append({
#             "isrctnId": text("isrctnId"),
#             "title": text("title"),
#             "status": text("recruitmentStatus"),
#             "lastEdited": text("lastEdited"),
#         })
#     return trials

# parse_trials(out)