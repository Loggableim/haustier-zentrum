#!/usr/bin/env python3
"""Validate every JSON-LD block in every article and write a portable CSV report."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART_DIR = ROOT / "artikel"
REPORT = ROOT / "validation_report.csv"

results = []
for fp in sorted(ART_DIR.glob("*.html")):
    text = fp.read_text(encoding="utf-8")
    blocks = list(re.finditer(
        r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        text, re.DOTALL | re.IGNORECASE))
    if not blocks:
        results.append((fp.name, "MISSING", "No JSON-LD script block"))
        continue
    for index, match in enumerate(blocks, 1):
        try:
            json.loads(match.group(1))
            results.append((fp.name, "OK", f"block {index}"))
        except (json.JSONDecodeError, TypeError) as error:
            results.append((fp.name, "ERROR", f"block {index}: {error}"))

with REPORT.open("w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["file", "status", "error"])
    writer.writerows(results)
print("Summary:", {status: sum(1 for _, s, _ in results if s == status)
                   for status in ("OK", "ERROR", "MISSING")})
if any(status != "OK" for _, status, _ in results):
    raise SystemExit(1)
