#!/bin/bash
# Auto-Deploy Script — Haustierzentrum
#
# Reihenfolge:
#   1. Refresh Sitemap + canonicals (idempotent)
#   2. Generate RSS feed
#   3. Git add + commit + push
#
# `set -e` sorgt dafür, dass bei Fehler sofort abgebrochen wird.
# `python3` ist Fallback falls `python` nicht verfügbar (Linux/Mac).

set -e
cd "$(dirname "$0")"

# Python finden (Windows: python, Linux: python3)
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then
    echo "ERROR: Python nicht gefunden"
    exit 1
fi

echo "=== Deploy $(date +%Y-%m-%d\ %H:%M:%S) ==="
echo ""

# 1. Sitemap + canonicals refresh (legt sitemap.xml neu an wenn nötig)
echo "[1/3] Refreshing sitemap..."
$PY _refresh_indexing.py

# 2. RSS-Feed neu generieren
echo "[2/3] Generating RSS feed..."
$PY _generate_feed.py --quiet

# 3. Git commit + push
echo "[3/3] Committing + pushing..."

# Stat für Commit-Message
ARTICLE_COUNT=$(ls artikel/*.html 2>/dev/null | wc -l)
RSS_ITEMS=$(grep -c '<item>' rss.xml 2>/dev/null || echo 0)
SITEMAP_URLS=$(grep -c '<loc>' sitemap.xml 2>/dev/null || echo 0)

# Nur committen wenn es Änderungen gibt
if git diff --cached --quiet 2>/dev/null && git diff --quiet 2>/dev/null; then
    echo "Keine Änderungen — überspringe commit."
    exit 0
fi

git add -A
git commit -m "Auto: $ARTICLE_COUNT articles, $SITEMAP_URLS sitemap URLs, $RSS_ITEMS RSS items ($(date +%Y-%m-%d))"

# Bei parallelen Pushs holt pull --rebase die Remote-Commits
# und rebased unseren Commit drauf. Wenn Konflikte: Abbruch.
echo "Pulling remote changes (rebase)..."
if ! git pull --rebase --autostash; then
    echo ""
    echo "ERROR: git pull --rebase failed (likely merge conflicts)."
    echo "Resolve manually: git status, fix conflicts, then git rebase --continue"
    echo "After fixing, just run ./deploy.sh again."
    exit 1
fi

git push

echo ""
echo "--- DEPLOYED ---"