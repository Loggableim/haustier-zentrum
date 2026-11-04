#!/usr/bin/env bash
# Kompatibilitaetsaufruf fuer den bisherigen Einstiegspunkt.
set -euo pipefail
exec bash "$(dirname "${BASH_SOURCE[0]}")/deploy.sh" "$@"
