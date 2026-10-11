#!/usr/bin/env python3
"""Portfolio structural and simple publishing preflight (NOT a security audit)."""
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site';ART=ROOT/'artifacts'

class Structure(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.anchors=[];self.bad_images=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get('id'):self.ids.add(d['id'])
        if tag=='a' and d.get('href','').startswith('#'):self.anchors.append(d['href'][1:])
        if tag=='img' and not d.get('alt','').strip():self.bad_images.append(d.get('src','missing src'))


def main():
    errors=[];warnings=[]
    required=['index.html','styles.css','projects.json','assets/evidence_assistant_baseline_flow.png','assets/proposed_local_llm_architecture.png']
    for rel in required:
        if not (SITE/rel).is_file():errors.append('Required file missing: '+rel)
    if not errors:
        page=(SITE/'index.html').read_text(encoding='utf8');styles=(SITE/'styles.css').read_text(encoding='utf8')
        data=json.loads((SITE/'projects.json').read_text(encoding='utf8'))
        titles=[p.get('title') for p in data.get('projects',[])]
        if len(titles)!=3:errors.append('Expected exactly 3 portfolio projects')
        for title in titles:
            if title not in page:errors.append('Missing case study title in HTML: '+str(title))
        parser=Structure();parser.feed(page)
        for anchor in parser.anchors:
            if anchor and anchor not in parser.ids:errors.append('Broken internal anchor: #'+anchor)
        for x in parser.bad_images:errors.append('Image lacks alt text: '+x)
        if '@media' not in styles:errors.append('No responsive CSS media query found')
        if 'proposed, not implemented' not in page.lower() and 'future proposal' not in page.lower():errors.append('Local LLM not clearly identified as future design')
        if 'synthetic' not in page.lower():errors.append('Synthetic data label missing')
        public=(SITE/'index.html').read_text()+(SITE/'projects.json').read_text()
        patterns=[(r'/Users/[\w-]+/','home directory'),(r'/mnt/data/','private sandbox path'),
                  (r'(?i)@cfleads\.org','work email address'),
                  (r'(?i)(api[_ -]?key|password|secret)\s*[=:]\s*[\"\']?[^\s,]{9,}','possible credential'),
                  (r'(?i)sk-[A-Za-z0-9]{20,}','possible API token')]
        for pattern,name in patterns:
            if re.search(pattern,public):errors.append('Potential sensitive material: '+name)
        summary=data.get('summary',{})
        if summary.get('evaluated_at_utc') is None:
            warnings.append('Extended 20-case evaluation has not yet been executed on this installation.')
        elif not summary.get('all_pass'):
            warnings.append(f"Extended 20-case evaluation is not fully passing ({summary.get('pass',0)} passed; {summary.get('fail',0)} failed; {summary.get('blocked',0)} blocked). Not ready to claim a fully passed gold set.")
    success=not errors
    print('PASS: required files, case-study sections, media and sanitized project data are present.' if success else 'FAIL: publication preflight found errors.')
    for e in errors:print('ERROR:',e)
    for w in warnings:print('NOTICE:',w)
    ART.mkdir(exist_ok=True)
    report=f'''# Portfolio — Site Release Review

**Reviewed:** {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}  
**Structural check:** {'PASS' if success else 'FAIL'}  
**Purpose:** Review evidence presentation and basic site packaging, not production security approval.

## Verified in this local check

- The site contains its homepage, stylesheet, machine-readable project descriptions and two diagram PNGs: {'yes' if success else 'not fully verified'}.
- Three case studies and internal navigation links: {'present' if success else 'see errors below'}.
- The local-LLM diagram is identified as future/proposed work, not an implemented model: {'yes' if success else 'see errors below'}.
- Synthetic-data language is present: {'yes' if success else 'see errors below'}.
- No sensitive-string pattern defined by this **basic scan** was detected: {'yes' if success else 'see errors below'}.

## Unresolved issues

{chr(10).join('- '+x for x in errors) if errors else 'No structural errors detected.'}

## Publication notices

{chr(10).join('- '+x for x in warnings) if warnings else 'No blocked evaluation tests reported in the current site data.'}

## What this check does not guarantee

No exhaustive secrets scan (including Git history), security review, WCAG conformance assessment, third-party hosting policy review, or human review of all data in the public bundle has been completed by this check. **Inspect `site/` yourself before publishing.** The optional online site should contain only synthetic/public evidence and sanitized explanations.

## Preview

From the project root: `python -m http.server 8000 --directory site`, then open `http://localhost:8000`. Stop with Control+C.
'''
    (ART/'portfolio_release_report.md').write_text(report)
    sys.exit(0 if success else 1)

if __name__=='__main__':main()
