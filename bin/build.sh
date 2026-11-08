#!/usr/bin/env bash
set -euo pipefail
python3 tools/site.py generate
python3 tools/site.py cv
python3 -m unittest discover -s tests -v
bundle exec jekyll build --trace
python3 tools/site.py audit
