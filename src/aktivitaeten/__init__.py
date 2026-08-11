"""Aktivitaeten-Pipeline: Dateien rein -> strukturierte Excel-Liste raus.

Module:
    model     Datensatz-Definition (ein Eintrag = eine Aktivitaet)
    icsfile   Parser fuer Outlook-/Teams-Kalendereintraege (.ics)
    emlfile   Parser fuer E-Mails (.eml)
    andere    Fallback fuer Screenshots, PDFs, Notizen, Office-Dateien
    felder    Heuristiken: Firma, Kontakt, Geldbetraege, Akquise-Felder
    registry  Persistenter Speicher inkl. Dedup und Update-Erkennung
    excel     Formatierte Excel-Mappe (mehrere Blaetter)
    cli       Einstiegspunkt
"""

__all__ = ["model", "icsfile", "emlfile", "andere", "felder", "registry", "excel", "cli"]
