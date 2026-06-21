#!/usr/bin/env python3
"""Add author/reviewer metadata and visible box to each article.

The script:
1. Scans all *.html in artikel/
2. Adds a visible box after the medical disclaimer if present, otherwise before the first <h1>
3. Updates the BlogPosting JSON‑LD to include:
   - "reviewer": {"@type":"Person","name":""}
   - "lastReviewed": "YYYY‑MM‑DD"
   - "sources": []
4. Writes back the file.
"""

import json, datetime
from pathlib import Path

ART_DIR = Path(r"C:\sidekick\home\spaces\haustier-zentrum\artikel")

def process_file(file_path: Path):
    text = file_path.read_text(encoding='utf-8')
    # Insert visible box
    box_html = (
        '<div class="author-reviewer-box" style="border-top:1px solid #ccc;padding-top:1rem;margin-top:1rem;"'>
        '<p><strong>Autor:</strong> Haustierzentrum Redaktion</p>'
        '<p><strong>Reviewer:</strong> (noch nicht geprüft)</p>'
        f'<p><strong>Letztes Review:</strong> {datetime.date.today().isoformat()}</p>'
        '</div>'
    )

    # Find first h1 or disclaimer
    if '<!-- MEDICAL DISCLAIMER -->' in text:
        insert_pos = text.find('<!-- MEDICAL DISCLAIMER -->') + len('<!-- MEDICAL DISCLAIMER -->')
        text = text[:insert_pos] + box_html + text[insert_pos:]
    else:
        h1_pos = text.find('<h1')
        if h1_pos != -1:
            text = text[:h1_pos] + box_html + text[h1_pos:]
        else:
            text = box_html + text

    # Update JSON-LD
    start = text.find('<script type="application/ld+json">')
    if start != -1:
        end = text.find('</script>', start)
        json_text = text[start+len('<script type="application/ld+json">'):end]
        try:
            data = json.loads(json_text)
            data['reviewer'] = {"@type":"Person","name":""}
            data['lastReviewed'] = datetime.date.today().isoformat()
            data['sources'] = []
            new_json = json.dumps(data, ensure_ascii=False, indent=2)
            text = text[:start+len('<script type="application/ld+json">')] + new_json + text[end:]
        except Exception:
            pass
    file_path.write_text(text, encoding='utf-8')

for f in ART_DIR.glob('*.html'):
    process_file(f)
print('Processed', len(list(ART_DIR.glob('*.html'))), 'files')
