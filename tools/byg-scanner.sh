#!/bin/sh
# Bygger js/scan.js: en lille stregkodelæser til browsere uden BarcodeDetector (fx iPhone og Firefox).
# Kræver Node. Kør fra repoets rod: sh tools/byg-scanner.sh
# Bygget af @zxing/library 0.23.0 (Apache-2.0) med esbuild. Kun læserne til EAN/UPC og Code 128 kommer med.
set -e
D=$(mktemp -d)
cp tools/scanner-entry.js "$D/entry.js"
( cd "$D" && npm init -y >/dev/null && npm install --silent @zxing/library@0.23.0 esbuild@0.24.0 \
  && npx esbuild entry.js --bundle --minify --format=iife --legal-comments=none --outfile=scan.js )
{ echo '/* Stregkodelæser til ølrating.dk. Bygget af @zxing/library 0.23.0 (Apache-2.0, https://github.com/zxing-js/library) med tools/byg-scanner.sh */'; cat "$D/scan.js"; } > js/scan.js
echo "js/scan.js: $(wc -c < js/scan.js) bytes"
