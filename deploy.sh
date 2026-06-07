#!/bin/bash
# Auto-Deploy Script — Blog Automation Framework
cd "$(dirname "$0")"
git add -A
git commit -m "Auto: Blog-Framework Update $(date +%Y-%m-%d)"
git push
echo "--- DEPLOYED ---"
