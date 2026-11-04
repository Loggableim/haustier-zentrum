#!/usr/bin/env bash
# Ohne --push nur lokal vorbereiten. QA_APPROVED_COMMIT erst nach Merles Freigabe setzen.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
mode=${1:---prepare}
case "$mode" in --prepare|--push) ;; *) echo 'Aufruf: bash deploy.sh [--prepare|--push]' >&2; exit 2 ;; esac
PY=${PYTHON:-$(command -v python3 || command -v python || true)}
if [[ -z "$PY" ]]; then echo 'Python 3 fehlt.' >&2; exit 1; fi
if [[ "$mode" == --push ]]; then
    [[ "$(git branch --show-current)" == main ]] || { echo 'Push nur von main.' >&2; exit 1; }
    [[ "${QA_APPROVED_COMMIT:-}" == "$(git rev-parse HEAD)" ]] || { echo 'Merles QA-Freigabe fuer diesen Commit fehlt (QA_APPROVED_COMMIT).' >&2; exit 1; }
    [[ -z "$(git status --porcelain)" ]] || { echo 'Vor Push alle geprueften Aenderungen lokal committen.' >&2; exit 1; }
    "$PY" _refresh_indexing.py --dry-run
    "$PY" _generate_feed.py --dry-run
    "$PY" _build_public.py
    "$PY" _check_release.py dist
    git push origin HEAD:main
    echo 'Push erfolgt; Deployment-Ergebnis in GitHub Actions pruefen.'
else
    "$PY" _refresh_indexing.py --dry-run
    "$PY" _generate_feed.py --dry-run
    "$PY" _refresh_indexing.py
    "$PY" _generate_feed.py
    "$PY" _build_public.py
    "$PY" _check_release.py dist
    echo 'Lokal vorbereitet. Aenderungen pruefen und gezielt committen; kein Push ausgefuehrt.'
fi
