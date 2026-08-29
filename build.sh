#!/bin/sh
# Baut aus tracker.html (Artifact-Format, ohne <html>-Rahmen) die
# eigenständige index.html, die sich lokal im Browser öffnen lässt.
# Getrennt wird an der Marker-Zeile <div id="root"></div>:
# alles davor -> <head>, alles ab dort -> <body>.
set -e
cd "$(dirname "$0")"
python3 - <<'PY'
src = open("tracker.html").read()
marker = '<div id="root"></div>'
head, body = src.split(marker, 1)
open("index.html", "w").write(
    '<!doctype html>\n<html lang="de">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<style>:root{color-scheme:light dark}body{margin:0}'
    'img{max-width:100%}[hidden]{display:none!important}</style>\n'
    + head.rstrip() + '\n</head>\n<body>\n' + marker + body.rstrip()
    + '\n</body>\n</html>\n'
)
print("index.html gebaut")
PY
