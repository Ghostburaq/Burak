# MiT-Designsystem, Masse und Raster

Quelle: Original-Master "Präsentation Strom CH" der Mobil in Time AG,
extrahiert aus der Vorlage von Sascha Promberger. Folienformat 16:9,
13.333 x 7.5 Zoll (12192000 x 6858000 EMU).

## Farben

| Zweck | Hex | Einsatz |
|---|---|---|
| MiT-Rot | E00036 | Eyebrow, Nummernfelder, Tabellenkopf, Highlight-Kacheln, Akzentstriche |
| Rot-Varianten im Original | E3022E, E4022E | nur in Altfolien, nicht neu verwenden |
| Dunkelrot | AA0223, 720117 | Schattierungen in Originalgrafiken |
| Kachelgrau | 58595B | Standardkachel, Fliesstext auf Weiss |
| Grau zweite Stufe | 3C3C3B | abgesetzte Kacheln (z. B. "gestrichen") |
| Text auf dunkel | E6E6E6 | Fliesstext in Kacheln |
| Helles Band | F2F2F2 | Randbemerkungen, Hinweise unter Tabellen |
| Zebrazeilen | FFFFFF / F4F4F4 | Tabellenkörper |
| Aggreko-Blau | 1A569D, 17549C, 6E9FD5 | nur wo Aggreko-Grafiken übernommen werden |
| Titel | 000000 | Folientitel |

## Schriften

- Major (Titel): **Alata**
- Minor (Fliesstext): **IBM Plex Sans**
- Beide stehen im Theme des Masters. Nicht überschreiben. Fallback bei
  fehlender Installation: Calibri.

Grössen, die sich bewährt haben:

| Element | pt |
|---|---|
| Titelfolie Haupttitel | 40 |
| Folientitel | 28 / 26 / 22 je nach Länge |
| Eyebrow (rot, Versalien, Laufweite 1.6) | 10.5 |
| Kachelüberschrift | 16 |
| Kacheltext | 12.5 |
| Kennzahl | 40 |
| Kennzahl-Label | 11.5 |
| Tabellenkopf und -körper | 10.5 bis 12 |
| Fusszeile und Foliennummer | 8.5 |
| Schlussfolie Kernsätze | 24 |

## Raster (Zoll)

```
Linker Rand Inhalt        0.47
Rechter Rand Inhalt      12.40   (danach graues Dreieck)
Titelzone links           1.74   (rechts vom roten Streifen)
Titelzone Breite          8.95   (endet vor dem Logo bei 10.69)
Eyebrow                   y=0.40
Titel                     y=0.72, Höhe 1.00
Roter Akzentstrich        y=1.72, 1.10 x 0.045
Inhalt oben               y=2.05
Inhalt unten              y=6.70
Fusszeile                 y=6.95, Foliennummer rechts bei x=11.10
Logo (aus dem Layout)     x=10.78, y=0.55, 1.93 x 0.65
```

Spaltenraster mit 0.22" Abstand bei Breite 11.93":

| Spalten | Breite |
|---|---|
| 2 | 5.855 |
| 3 | 3.83 |
| 4 | 2.82 |
| 5 | 2.21 |
| 6 | 1.80 |

## Sperrflächen

Die Hintergrundgrafiken sind Teil der Layouts und lassen sich nicht
verschieben. Drei Zonen sind tabu:

1. **Roter Keil der Titelfolie**: von x=0 bis 4.37 oben, bis 2.07 unten.
   Inhalt der Titelfolie beginnt erst bei x=4.55. Im Keil selbst funktioniert
   weisse Typo, dort stehen die Kennzahlen.
2. **Roter Streifen der Inhaltsfolien**: von x=0 bis 1.11 oben, läuft bei
   y=3.33 aus. Deckende Kacheln dürfen darüber, Text nicht.
3. **Graues Dreieck unten rechts**: Spitze bei (13.18, 3.63), untere Kante bei
   (12.15, 7.50). Nichts über x=12.40 platzieren.
4. **Rotes Parallelogramm der Abschlussfolie**: obere Kante x=4.81 bis 10.71,
   untere Kante x=3.01 bis 8.74. Text zwischen x=4.60 und 9.90, weiss.

## Layouts im Master

| Nr. | Name | Verwendung |
|---|---|---|
| 1 | Titelfolie | Cover, roter Keil links |
| 2 | Text und Bild | 4 Bild- und 4 Textplatzhalter |
| 3 | Titel und Inhalt | Standard für alle Inhaltsfolien |
| 4 | 3-Spaltiger Text und Bild | Bild-Text-Kombinationen |
| 5 | Zwei Inhalte | zweispaltig |
| 6 | 1_Titel und Inhalt | mehrere Platzhalter |
| 7 | 2-spaltiger Text Grid | Textraster |
| 8 | Nur Titel | Abschnitt und Schluss, rotes Parallelogramm |
| 9 | Inhalt mit Überschrift | |
| 10 | Abschnittsüberschrift | |
| 11 | Vergleich | |
| 12 | Leer | |
| 13/14 | vertikale Varianten | selten |

`mit_deck.py` nutzt 1, 3 und 8 und setzt alle Elemente selbst, weil die
Platzhalter für dichte Inhalte zu grob sind.

## Folientypen, die sich bewährt haben

- **Kennzahlenreihe plus Aussagenband**: vier bis fünf Zahlen, darunter ein
  dunkles Band mit der Folgerung. Wirkt, weil die Zahl zuerst kommt.
- **Kachelraster 3x1 oder 3x2**: eine Kachel rot, wenn eine davon die Botschaft
  trägt.
- **Prozesskette**: vier Nummernfelder auf einer Linie, darunter Titel und zwei
  Zeilen Text.
- **Phasenband**: sechs schmale Kacheln nebeneinander, die relevanten rot.
  Zeigt auf einen Blick, wo MiT andockt.
- **Tabelle mit rotem Kopf**: für Kontakt-, Projekt- und Firmenlisten.
- **Abschlussfolie**: drei kurze Sätze im roten Parallelogramm. Kein vierter.
