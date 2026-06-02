#!/bin/bash
cd /c/HermesPortable/home/scripts/blog-automation/haustier-zentrum && \
git add artikel/katzenfutter-vergleich-2026.html sitemap.xml && \
git commit -m "Neuer Artikel: Katzenfutter Vergleich 2026 – Nassfutter vs. Trockenfutter" && \
git push
echo "--- DONE ---"
