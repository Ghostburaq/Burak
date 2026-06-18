Attribute VB_Name = "PdfButton"
'==============================================================================
'  Offerte als PDF speichern - auf Knopfdruck
'  Modul fuer die "Offerten_Master_Vorlage" (Excel, Windows & Mac)
'
'  Einbau:  Datei als .xlsm speichern  ->  Alt+F11  ->  Datei > Importieren
'           -> PdfButton.bas. Danach eine Schaltflaeche einfuegen
'           (Entwicklertools > Einfuegen > Schaltflaeche) und das Makro
'           "Offerte_Als_PDF" zuweisen. Details: PDF_Knopf_Anleitung.md
'==============================================================================
Option Explicit

Public Sub Offerte_Als_PDF()
    Dim ws As Worksheet
    Dim pfad As String, datei As String, nr As String
    Dim voll As String

    On Error GoTo Fehler
    Set ws = ThisWorkbook.Worksheets("Offerte")

    ' Offerte-Nr. aus Zelle G8 als Dateiname (Sonderzeichen entfernen)
    nr = CStr(ws.Range("G8").Value)
    nr = Saeubern(nr)
    If Len(nr) = 0 Then nr = "Offerte"

    ' Speicherort = Ordner der Arbeitsmappe (Fallback: Dokumente)
    pfad = ThisWorkbook.Path
    If Len(pfad) = 0 Then pfad = Environ$("USERPROFILE") & "\Documents"
    voll = pfad & Application.PathSeparator & nr & ".pdf"

    Application.ScreenUpdating = False

    ' Nur das Blatt "Offerte" exportieren (nutzt den gesetzten Druckbereich)
    ws.ExportAsFixedFormat _
        Type:=xlTypePDF, _
        Filename:=voll, _
        Quality:=xlQualityStandard, _
        IncludeDocProperties:=True, _
        IgnorePrintAreas:=False, _
        OpenAfterPublish:=True

    Application.ScreenUpdating = True
    MsgBox "PDF erstellt:" & vbCrLf & voll, vbInformation, "Offerte gespeichert"
    Exit Sub

Fehler:
    Application.ScreenUpdating = True
    MsgBox "PDF konnte nicht erstellt werden:" & vbCrLf & Err.Description, _
           vbExclamation, "Fehler"
End Sub

' Hilfsfunktion: fuer Dateinamen unzulaessige Zeichen ersetzen
Private Function Saeubern(s As String) As String
    Dim bad As Variant, b As Variant, r As String
    r = Trim$(s)
    bad = Array("/", "\", ":", "*", "?", """", "<", ">", "|")
    For Each b In bad
        r = Replace(r, CStr(b), "-")
    Next b
    r = Replace(r, " ", "_")
    Saeubern = r
End Function
