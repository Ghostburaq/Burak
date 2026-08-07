#!/bin/sh
# Erzeugt die Masterdatei komplett neu.
# Erwartet quelle_stand_vor_update.xlsx als original.xlsx im selben Ordner.
set -e
python3 build_master_reporting.py   # Stufe 1: Aggreko-Wahrscheinlichkeitsmodell
python3 build_governance.py         # Stufe 2: Marge, Nachweis, Varianten, Definitionen
echo "Fertig. Datei jetzt einmal in Excel oder LibreOffice öffnen und neu"
echo "berechnen lassen, damit die zwischengespeicherten Werte stimmen."
