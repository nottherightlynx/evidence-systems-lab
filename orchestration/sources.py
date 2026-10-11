"""Bounded public metadata and explicitly synthetic state fixtures."""
from pathlib import Path
from datetime import datetime, timezone
import json, requests
ROOT=Path(__file__).resolve().parent.parent

def load_sources(fetch_federal=False):
    results=[]
    for name in ('state_A.json','state_B.json'):
        path=ROOT/'data/synthetic'/name
        results.append({'kind':'simulation','filename':name,'payload':json.loads(path.read_text(encoding='utf8'))})
    if fetch_federal:
        url='https://www.federalregister.gov/api/v1/documents.json'
        # Federal Register API: accept actual public records only after successful HTTP validation.
        response=requests.get(url,params={'per_page':10,'order':'newest'},timeout=20,
                              headers={'User-Agent':'EvidenceSystemsLabDemo/0.1 (research portfolio)'})
        response.raise_for_status()
        data=response.json()
        if not isinstance(data.get('results'),list):
            raise ValueError('Official API response missing results')
        results.append({'kind':'official_public_api','filename':url,'payload':data})
    return results
