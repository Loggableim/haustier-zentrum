# -*- coding: utf-8 -*-
"""Markiert Queue-Eintraege als Fertig (zeilenweise, robust, LF-stabil)."""
import re, os, io

path = 'ARTICLE_QUEUE.md'
q = io.open(path, 'r', encoding='utf-8', newline='').read()
art = set(os.listdir('artikel'))
alias = {
    'katzen-kastration-ablauf-kosten-nachsorge': 'katzen-kastration-sterilisation.html',
    'katzen-fellpflege-buersten-knoten': 'katzen-fellpflege-buersten.html',
    'katzen-balkon-sichern-gefahrlos': 'katzen-balkon-sichern.html',
    'frettchen-haltung-musst-du-wissen': 'frettchen-haustier-haltung-pflege-kosten.html',
    'aquarium-pflanzen-arten-pflege': 'aquarium-pflanzen-einsteiger.html',
    'allergiker-haustiere-besten-rassen': 'allergiker-haustiere.html',
    'ragdoll-rasseguide': 'ragdoll-katze-rasseguide.html',
}
rows = re.findall(r'^\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*`([a-z0-9\-]+)`', q, re.M)
today = '26.11.2026'
done = [(num, slug) for num, topic, _, slug in rows if slug + '.html' in art or slug in alias]

lines = q.splitlines(True)  # keep original line endings
out, changed = [], 0
for line in lines:
    if 'Bereit' in line:
        for num, slug in done:
            if '`' + slug + '`' in line and re.search(r'\|\s*' + num + r'\s*\|', line):
                line = line.replace('Bereit', 'Fertig ' + today)
                changed += 1
                break
    out.append(line)
io.open(path, 'w', encoding='utf-8', newline='').write(''.join(out))
print('Zeilen aktualisiert:', changed)

q2 = io.open(path, 'r', encoding='utf-8', newline='').read()
still = [s for _, _, _, s in rows if (s + '.html' in art or s in alias) and re.search(r'\|\s*\d+\s*\|\s*[^|]*Bereit[^|]*`\s*' + s, q2)]
print('Noch als Bereit markiert (sollte 0 sein):', len(still))
