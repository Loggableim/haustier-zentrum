# -*- coding: utf-8 -*-
"""Queue-Abgleich: prueft, welche ARTICLE_QUEUE-Slugs bereits als Artikel existieren."""
import re, os, io

q = io.open('ARTICLE_QUEUE.md', encoding='utf-8').read()
rows = re.findall(r'^\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*`([a-z0-9\-]+)`', q, re.M)
slugs = [r[3] for r in rows]
art = set(os.listdir('artikel'))

print('Queue-Zeilen:', len(slugs))
print('Einzigartige Slugs:', len(set(slugs)))

existing, missing = [], []
for s in sorted(set(slugs)):
    if s + '.html' in art:
        existing.append(s)
    else:
        missing.append(s)

print('Existierend:', len(existing))
print('Fehlend:', len(missing))
print()
print('--- Existierend (als Fertig zu markieren) ---')
nums = {r[3]: r[0] for r in rows}
for s in existing:
    print(f"#{nums[s]}\t{s}")
print()
print('--- Fehlend (Bereit-Status korrekt) ---')
print(', '.join(missing))
