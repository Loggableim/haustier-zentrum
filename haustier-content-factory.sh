#!/usr/bin/env bash
# Haustier Content Factory cron wrapper
# Generates 1 article + 1 hero image per run using MiniMax-M3
cd /c/sidekick/home/spaces/haustier-zentrum || exit 1
python content_factory.py 2>&1
