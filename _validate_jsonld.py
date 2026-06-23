#!/usr/bin/env python3
"""Validate JSON‑LD blocks in all article files.

The script scans every *.html file in the artikel/ directory, extracts
any <script type="application/ld+json"> blocks and attempts to parse
them with json.loads().  It prints a summary of the results and writes
a CSV report to `validation_report.csv` in the workspace.
"""

import json, csv, pathlib

ART_DIR = pathlib.Path(r"C:\\sidekick\\home\\spaces\\haustier-zentrum\\artikel")
REPORT = pathlib.Path(r"C:\\sidekick\\home\\spaces\\haustier-zentrum\\validation_report.csv")

results = []
for fp in ART_DIR.glob('*.html'):
    text = fp.read_text(encoding='utf-8')
    start = text.find('<script type="application/ld+json">')
    if start == -1:
        results.append((fp.name, 'MISSING', ''))
        continue
    end = text.find('</script>', start)
    json_text = text[start+len('<script type="application/ld+json">'):end]
    try:
        json.loads(json_text)
        results.append((fp.name, 'OK', ''))
    except Exception as e:
        results.append((fp.name, 'ERROR', str(e)))

# write CSV
with REPORT.open('w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['file', 'status', 'error'])
    writer.writerows(results)

print('Validation complete – see', REPORT)
print('Summary: OK', sum(1 for _,s,_ in results if s=='OK'),
      'ERROR', sum(1 for _,s,_ in results if s=='ERROR'),
      'MISSING', sum(1 for _,s,_ in results if s=='MISSING'))
